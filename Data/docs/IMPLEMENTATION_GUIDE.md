# CDC Implementation Guide

**Document Version**: 1.0  
**Last Updated**: 2024-12-29  
**Status**: Planning Phase

## Prerequisites

### Infrastructure Requirements

1. **Apache Kafka Cluster**
   - Minimum 3 brokers (production)
   - Kafka version: 3.0+
   - Storage: 500GB+ per broker
   - Network: Low latency between databases and Kafka

2. **Kafka Connect**
   - Kafka Connect distributed mode
   - Debezium PostgreSQL connector plugin
   - Memory: 2-4 GB per connector

3. **Apache Ranger**
   - Ranger Admin server
   - Ranger Kafka plugin
   - Integration with existing security infrastructure

4. **Database Requirements**
   - PostgreSQL 12+ with logical replication support
   - WAL level: logical
   - Adequate disk space for WAL retention

### Software Versions

- PostgreSQL: 14+
- Debezium: 2.0+
- Apache Kafka: 3.0+
- Apache Ranger: 2.3+
- Java: 11+

## Step-by-Step Setup

### Step 1: Database Configuration

#### 1.1 Enable Logical Replication on smart_warehouse

```sql
-- Connect as postgres superuser
ALTER SYSTEM SET wal_level = logical;
ALTER SYSTEM SET max_replication_slots = 10;
ALTER SYSTEM SET max_wal_senders = 10;

-- Restart PostgreSQL
-- Then verify:
SHOW wal_level;  -- Should return 'logical'
```

#### 1.2 Enable Logical Replication on smart_citizen

Repeat the same steps for smart_citizen database.

#### 1.3 Create Debezium User

```sql
-- On smart_warehouse
CREATE USER debezium_user WITH REPLICATION PASSWORD 'secure_password_change_me';
GRANT CONNECT ON DATABASE smart_warehouse TO debezium_user;
GRANT USAGE ON SCHEMA public TO debezium_user;
GRANT USAGE ON SCHEMA eligibility TO debezium_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO debezium_user;
GRANT SELECT ON ALL TABLES IN SCHEMA eligibility TO debezium_user;

-- On smart_citizen
CREATE USER debezium_user WITH REPLICATION PASSWORD 'secure_password_change_me';
GRANT CONNECT ON DATABASE smart_citizen TO debezium_user;
GRANT USAGE ON SCHEMA public TO debezium_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO debezium_user;
```

### Step 2: Kafka Setup

#### 2.1 Install Apache Kafka

```bash
# Download and extract Kafka
wget https://downloads.apache.org/kafka/3.5.0/kafka_2.13-3.5.0.tgz
tar -xzf kafka_2.13-3.5.0.tgz
cd kafka_2.13-3.5.0
```

#### 2.2 Configure Kafka

Edit `config/server.properties`:
```properties
broker.id=1
listeners=PLAINTEXT://localhost:9092
log.dirs=/var/kafka-logs
num.partitions=3
default.replication.factor=3
min.insync.replicas=2
```

#### 2.3 Start Kafka

```bash
# Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka broker
bin/kafka-server-start.sh config/server.properties
```

### Step 3: Kafka Connect Setup

#### 3.1 Install Debezium Connector

```bash
# Download Debezium PostgreSQL connector
wget https://repo1.maven.org/maven2/io/debezium/debezium-connector-postgres/2.3.0.Final/debezium-connector-postgres-2.3.0.Final-plugin.tar.gz
tar -xzf debezium-connector-postgres-2.3.0.Final-plugin.tar.gz
mv debezium-connector-postgres /opt/kafka/plugins/
```

#### 3.2 Configure Kafka Connect

Edit `config/connect-distributed.properties`:
```properties
bootstrap.servers=localhost:9092
group.id=connect-cluster
key.converter=org.apache.kafka.connect.json.JsonConverter
value.converter=org.apache.kafka.connect.json.JsonConverter
key.converter.schemas.enable=false
value.converter.schemas.enable=false
plugin.path=/opt/kafka/plugins
```

#### 3.3 Start Kafka Connect

```bash
bin/connect-distributed.sh config/connect-distributed.properties
```

### Step 4: Deploy Connectors

#### 4.1 Warehouse to Citizen Connector

```bash
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @../config/warehouse-to-citizen-connector.json
```

#### 4.2 Citizen to Warehouse Connector

```bash
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @../config/citizen-to-warehouse-connector.json
```

### Step 5: Verify Connectors

```bash
# Check connector status
curl http://localhost:8083/connectors/warehouse-to-citizen-connector/status

# List all connectors
curl http://localhost:8083/connectors
```

### Step 6: Test Data Flow

#### 6.1 Create Test Record in Warehouse

```sql
-- Insert test record in smart_warehouse
INSERT INTO eligibility.eligibility_snapshots (
    family_id, scheme_code, evaluation_status, 
    eligibility_score, confidence_score
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    'CHIRANJEEVI',
    'RULE_ELIGIBLE',
    0.95,
    0.90
);
```

#### 6.2 Verify Kafka Topic

```bash
# Consume from Kafka topic to verify
bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic warehouse-to-citizen-cdc.eligibility_snapshots \
  --from-beginning
```

### Step 7: Implement Consumers

See example consumer code in `scripts/consumers/` directory.

---

## Troubleshooting

### Common Issues

#### Issue 1: Connector Fails to Start
**Symptom**: Connector status shows FAILED

**Solutions**:
- Check PostgreSQL WAL is set to 'logical'
- Verify Debezium user has correct permissions
- Check network connectivity between Kafka Connect and database
- Review connector logs: `logs/connect.log`

#### Issue 2: High Consumer Lag
**Symptom**: Consumer lag increasing continuously

**Solutions**:
- Increase consumer instances
- Check consumer processing speed
- Verify no blocking operations in consumer
- Consider increasing partition count

#### Issue 3: Data Not Syncing
**Symptom**: Changes in source not appearing in Kafka

**Solutions**:
- Verify replication slot is created: `SELECT * FROM pg_replication_slots;`
- Check WAL sender is running: `SELECT * FROM pg_stat_replication;`
- Verify table is included in connector config
- Check for schema mismatches

---

## Performance Tuning

### Kafka Tuning

```properties
# Increase throughput
num.network.threads=8
num.io.threads=16
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
```

### Debezium Tuning

```json
{
  "snapshot.mode": "never",  // Skip initial snapshot for large tables
  "snapshot.fetch.size": 2000,
  "max.batch.size": 2048,
  "max.queue.size": 8192
}
```

---

## Rollback Procedure

If issues occur, follow these steps:

1. **Pause Connectors**:
   ```bash
   curl -X PUT http://localhost:8083/connectors/warehouse-to-citizen-connector/pause
   ```

2. **Stop Consumers**: Stop all consumer applications

3. **Review Errors**: Check logs and DLQ for error patterns

4. **Fix Issues**: Address root causes

5. **Resume Connectors**:
   ```bash
   curl -X PUT http://localhost:8083/connectors/warehouse-to-citizen-connector/resume
   ```

---

## Next Steps

After successful setup:
1. Implement monitoring and alerting (see main strategy document)
2. Configure Apache Ranger data masking
3. Set up consumer applications
4. Conduct load testing
5. Plan production deployment


/**
 * Rule Management Component
 * Frontend interface for managing eligibility rules
 * Use Case: AI-PLATFORM-03
 */

import React, { useState, useEffect } from 'react';
import { Button, Table, Modal, Form, Input, Select, DatePicker, Switch, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, HistoryOutlined, TestTubeOutlined } from '@ant-design/icons';

const { Option } = Select;
const { TextArea } = Input;

interface Rule {
  rule_id: number;
  scheme_id: string;
  rule_name: string;
  rule_type: string;
  rule_expression: string;
  rule_operator: string;
  rule_value: string;
  is_mandatory: boolean;
  priority: number;
  version: number;
  effective_from: string;
  effective_to?: string;
}

interface RuleManagementProps {
  schemeId?: string;
}

const RuleManagement: React.FC<RuleManagementProps> = ({ schemeId }) => {
  const [rules, setRules] = useState<Rule[]>([]);
  const [schemes, setSchemes] = useState<any[]>([]);
  const [selectedScheme, setSelectedScheme] = useState<string>(schemeId || '');
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingRule, setEditingRule] = useState<Rule | null>(null);
  const [form] = Form.useForm();

  // Load schemes and rules
  useEffect(() => {
    loadSchemes();
    if (selectedScheme) {
      loadRules(selectedScheme);
    }
  }, [selectedScheme]);

  const loadSchemes = async () => {
    try {
      const response = await fetch('/api/v1/admin/rules/schemes');
      const data = await response.json();
      setSchemes(data);
    } catch (error) {
      message.error('Failed to load schemes');
    }
  };

  const loadRules = async (schemeId: string) => {
    try {
      const response = await fetch(`/api/v1/admin/rules/scheme/${schemeId}`);
      const data = await response.json();
      setRules(data.rules || []);
    } catch (error) {
      message.error('Failed to load rules');
    }
  };

  const handleAddRule = () => {
    setEditingRule(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleEditRule = (rule: Rule) => {
    setEditingRule(rule);
    form.setFieldsValue({
      ...rule,
      effective_from: rule.effective_from ? dayjs(rule.effective_from) : dayjs(),
      effective_to: rule.effective_to ? dayjs(rule.effective_to) : null,
    });
    setIsModalVisible(true);
  };

  const handleDeleteRule = async (ruleId: number) => {
    try {
      await fetch(`/api/v1/admin/rules/${ruleId}`, { method: 'DELETE' });
      message.success('Rule deleted successfully');
      loadRules(selectedScheme);
    } catch (error) {
      message.error('Failed to delete rule');
    }
  };

  const handleSaveRule = async (values: any) => {
    try {
      const payload = {
        ...values,
        effective_from: values.effective_from?.format('YYYY-MM-DD'),
        effective_to: values.effective_to?.format('YYYY-MM-DD'),
        scheme_id: selectedScheme,
      };

      if (editingRule) {
        await fetch(`/api/v1/admin/rules/${editingRule.rule_id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        message.success('Rule updated successfully');
      } else {
        await fetch('/api/v1/admin/rules', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        message.success('Rule created successfully');
      }

      setIsModalVisible(false);
      loadRules(selectedScheme);
    } catch (error) {
      message.error('Failed to save rule');
    }
  };

  const handleTestRule = async (rule: Rule) => {
    try {
      const response = await fetch('/api/v1/admin/rules/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          rule_expression: rule.rule_expression,
          test_data: {
            age: 65,
            income_band: 'LOW',
            gender: 'M',
          },
        }),
      });
      const result = await response.json();
      message.info(`Test result: ${result.passed ? 'PASSED' : 'FAILED'}`);
    } catch (error) {
      message.error('Failed to test rule');
    }
  };

  const columns = [
    {
      title: 'Rule Name',
      dataIndex: 'rule_name',
      key: 'rule_name',
    },
    {
      title: 'Type',
      dataIndex: 'rule_type',
      key: 'rule_type',
    },
    {
      title: 'Expression',
      dataIndex: 'rule_expression',
      key: 'rule_expression',
      ellipsis: true,
    },
    {
      title: 'Mandatory',
      dataIndex: 'is_mandatory',
      key: 'is_mandatory',
      render: (mandatory: boolean) => (mandatory ? 'Yes' : 'No'),
    },
    {
      title: 'Version',
      dataIndex: 'version',
      key: 'version',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: Rule) => (
        <div>
          <Button
            icon={<EditOutlined />}
            size="small"
            onClick={() => handleEditRule(record)}
            style={{ marginRight: 8 }}
          />
          <Button
            icon={<TestTubeOutlined />}
            size="small"
            onClick={() => handleTestRule(record)}
            style={{ marginRight: 8 }}
          />
          <Button
            icon={<HistoryOutlined />}
            size="small"
            href={`/admin/rules/${record.rule_id}/versions`}
            style={{ marginRight: 8 }}
          />
          <Button
            icon={<DeleteOutlined />}
            size="small"
            danger
            onClick={() => handleDeleteRule(record.rule_id)}
          />
        </div>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Select
          value={selectedScheme}
          onChange={setSelectedScheme}
          placeholder="Select Scheme"
          style={{ width: 300 }}
        >
          {schemes.map((scheme) => (
            <Option key={scheme.scheme_id} value={scheme.scheme_id}>
              {scheme.scheme_name}
            </Option>
          ))}
        </Select>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAddRule}>
          Add Rule
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={rules}
        rowKey="rule_id"
        pagination={{ pageSize: 20 }}
      />

      <Modal
        title={editingRule ? 'Edit Rule' : 'Add Rule'}
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        onOk={() => form.submit()}
        width={800}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSaveRule}
          initialValues={{
            is_mandatory: true,
            priority: 0,
            effective_from: dayjs(),
          }}
        >
          <Form.Item
            name="rule_name"
            label="Rule Name"
            rules={[{ required: true }]}
          >
            <Input placeholder="e.g., Age Requirement" />
          </Form.Item>

          <Form.Item
            name="rule_type"
            label="Rule Type"
            rules={[{ required: true }]}
          >
            <Select placeholder="Select rule type">
              <Option value="AGE">Age</Option>
              <Option value="INCOME">Income</Option>
              <Option value="GENDER">Gender</Option>
              <Option value="GEOGRAPHY">Geography</Option>
              <Option value="CATEGORY">Category/Caste</Option>
              <Option value="DISABILITY">Disability</Option>
              <Option value="HOUSEHOLD">Household Composition</Option>
              <Option value="MARITAL_STATUS">Marital Status</Option>
              <Option value="PRIOR_PARTICIPATION">Prior Participation</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="rule_operator"
            label="Operator"
            rules={[{ required: true }]}
          >
            <Select placeholder="Select operator">
              <Option value=">=">Greater than or equal (>=)</Option>
              <Option value="<=">Less than or equal (<=)</Option>
              <Option value="=">Equal (=)</Option>
              <Option value="IN">In (IN)</Option>
              <Option value="NOT_IN">Not In (NOT_IN)</Option>
              <Option value="DISTRICT_IN">District In (DISTRICT_IN)</Option>
              <Option value="BLOCK_IN">Block In (BLOCK_IN)</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="rule_value"
            label="Rule Value"
            rules={[{ required: true }]}
          >
            <Input placeholder="e.g., 60 or VERY_LOW,LOW" />
          </Form.Item>

          <Form.Item
            name="rule_expression"
            label="Rule Expression"
            rules={[{ required: true }]}
          >
            <TextArea
              rows={2}
              placeholder="e.g., age >= 60"
            />
          </Form.Item>

          <Form.Item
            name="is_mandatory"
            label="Mandatory"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="priority"
            label="Priority"
            rules={[{ required: true }]}
          >
            <Input type="number" placeholder="Higher = evaluated first" />
          </Form.Item>

          <Form.Item
            name="effective_from"
            label="Effective From"
            rules={[{ required: true }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="effective_to"
            label="Effective To (Optional)"
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

// Note: Import dayjs at top of file
import dayjs from 'dayjs';

export default RuleManagement;


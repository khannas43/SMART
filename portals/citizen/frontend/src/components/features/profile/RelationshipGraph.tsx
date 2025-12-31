import React, { useEffect, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Box, Paper, Typography, Chip, Stack, CircularProgress, Alert } from '@mui/material';

interface Node {
  id: number;
  gr_id: string;
  label: string;
  name: string;
  age?: number;
  gender?: string;
}

interface Link {
  source: number | Node;
  target: number | Node;
  relationship_type: string;
  label: string;
  type: string;
  weight?: number;
}

interface GraphData {
  nodes: Node[];
  links: Link[];
}

interface RelationshipType {
  label: string;
  icon: string;
  color: string;
  description: string;
}

interface RelationshipTypes {
  [key: string]: RelationshipType;
}

interface RelationshipGraphProps {
  grId: string;
  depth?: number;
  height?: number;
}

/**
 * Component to visualize citizen relationship network graph
 * Displays nodes (people) and edges (relationships) with labels and colors
 */
export const RelationshipGraph: React.FC<RelationshipGraphProps> = ({
  grId,
  depth = 2,
  height = 600,
}) => {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [relationshipTypes, setRelationshipTypes] = useState<RelationshipTypes>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const graphRef = useRef<any>();

  // Relationship type color mapping
  const getRelationshipColor = (type: string): string => {
    return relationshipTypes[type]?.color || '#68BDF6';
  };

  // Node color by gender
  const getNodeColor = (node: Node): string => {
    if (node.gender === 'FEMALE') return '#FF6B9D';
    if (node.gender === 'MALE') return '#68BDF6';
    return '#95A5A6';
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch relationship types legend
        const typesResponse = await fetch('/api/v1/profiles/graph/relationship-types');
        const types: RelationshipTypes = await typesResponse.json();
        setRelationshipTypes(types);

        // Fetch graph data
        const graphResponse = await fetch(
          `/api/v1/profiles/graph/family-network/${grId}?depth=${depth}`
        );
        if (!graphResponse.ok) {
          throw new Error('Failed to fetch graph data');
        }
        const data: GraphData = await graphResponse.json();
        setGraphData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load graph');
      } finally {
        setLoading(false);
      }
    };

    if (grId) {
      fetchData();
    }
  }, [grId, depth]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={height}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!graphData || graphData.nodes.length === 0) {
    return (
      <Alert severity="info" sx={{ m: 2 }}>
        No relationship data found.
      </Alert>
    );
  }

  return (
    <Box>
      {/* Relationship Type Legend */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          Relationship Types
        </Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          {Object.entries(relationshipTypes).map(([type, info]) => (
            <Chip
              key={type}
              label={`${info.icon} ${info.label}`}
              sx={{
                bgcolor: info.color,
                color: 'white',
                fontWeight: 'bold',
              }}
              size="small"
            />
          ))}
        </Stack>
      </Paper>

      {/* Graph Visualization */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Family & Relationship Network
        </Typography>
        <Box
          sx={{
            border: '1px solid #e0e0e0',
            borderRadius: 1,
            overflow: 'hidden',
          }}
        >
          <ForceGraph2D
            ref={graphRef}
            graphData={graphData}
            nodeLabel={(node: Node) => {
              const ageText = node.age ? ` (Age: ${node.age})` : '';
              return `${node.name}${ageText}`;
            }}
            nodeColor={(node: Node) => getNodeColor(node)}
            nodeVal={(node: Node) => {
              // Node size based on number of connections
              const nodeLinks = graphData.links.filter(
                (link) =>
                  (typeof link.source === 'object' && link.source.id === node.id) ||
                  (typeof link.target === 'object' && link.target.id === node.id) ||
                  link.source === node.id ||
                  link.target === node.id
              );
              return 5 + nodeLinks.length * 2;
            }}
            linkLabel={(link: Link) => {
              const typeInfo = relationshipTypes[link.type];
              return typeInfo
                ? `${typeInfo.icon} ${typeInfo.label}`
                : link.relationship_type;
            }}
            linkColor={(link: Link) => getRelationshipColor(link.type)}
            linkWidth={(link: Link) => (link.weight || 1) * 2}
            linkDirectionalArrowLength={6}
            linkDirectionalArrowRelPos={1}
            linkCurvature={0.2}
            cooldownTicks={100}
            onNodeHover={(node) => {
              if (node) {
                graphRef.current?.pauseAnimation();
              } else {
                graphRef.current?.resumeAnimation();
              }
            }}
            onNodeClick={(node: Node) => {
              // Could open profile details modal
              console.log('Clicked node:', node);
            }}
            width={800}
            height={height}
          />
        </Box>

        {/* Statistics */}
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Showing {graphData.nodes.length} people and {graphData.links.length} relationships
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default RelationshipGraph;


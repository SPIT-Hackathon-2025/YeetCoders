import React, { useState, useCallback, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import ReactFlow, {
  addEdge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  useReactFlow,
  ReactFlowProvider,
} from "reactflow";
import "reactflow/dist/style.css";
import Sidebar from "./Sidebar";

// If you're not using custom nodeTypes or edgeTypes, define them outside the component.
const nodeTypes = {};
const edgeTypes = {};

const WORKFLOW_STORAGE_KEY = "workflowData";

const WorkflowBuilderContent = () => {
  // Get workflowId from URL params (if present)
  const { workflowId } = useParams();
  const navigate = useNavigate();
  const { project } = useReactFlow();

  // State for workflow name and for nodes/edges
  const [workflowName, setWorkflowName] = useState("");
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
  }, []);

 // Function to update email in selected node
 const handleInputChange = (e, field) => {
  const value = e.target.value;
  setNodes((prevNodes) =>
    prevNodes.map((node) =>
      node.id === selectedNode.id
        ? { ...node, data: { ...node.data, [field]: value } }
        : node
    )
  );
};

  // Load workflow data either from backend (if workflowId exists) or from localStorage
  useEffect(() => {
    const loadWorkflow = async () => {
      if (workflowId) {
        // Fetch from backend
        try {
          const response = await fetch(`http://127.0.0.1:5000/get_workflow/${workflowId}`);
          if (!response.ok) throw new Error("Workflow not found on backend");
          const data = await response.json();
          setWorkflowName(data.templateName || "Unnamed Workflow");
          setNodes(data.nodes || []);
          setEdges(data.edges || []);
        } catch (error) {
          console.error("Error loading workflow from backend:", error);
        } finally {
          setLoading(false);
        }
      } else {
        // Load from localStorage if no workflowId is provided
        const savedWorkflow = localStorage.getItem(WORKFLOW_STORAGE_KEY);
        if (savedWorkflow) {
          try {
            const { nodes: savedNodes, edges: savedEdges, templateName } = JSON.parse(savedWorkflow);
            if (savedNodes && savedNodes.length > 0) setNodes(savedNodes);
            if (savedEdges && savedEdges.length > 0) setEdges(savedEdges);
            if (templateName) setWorkflowName(templateName);
          } catch (error) {
            console.error("Failed to parse workflow from localStorage:", error);
          }
        }
        setLoading(false);
      }
    };

    loadWorkflow();
  }, [workflowId, setNodes, setEdges]);

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onDragOver = (event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  };

  const onDrop = (event) => {
    event.preventDefault();
    const type = event.dataTransfer.getData("application/reactflow");
    if (!type) return;

    // Get canvas position to adjust coordinates
    const reactFlowBounds = event.currentTarget.getBoundingClientRect();
    const dropPosition = project({
      x: event.clientX - reactFlowBounds.left,
      y: event.clientY - reactFlowBounds.top,
    });

    const newNode = {
      id: `${Date.now()}`, // Using timestamp as a temporary ID
      type: "default",
      position: dropPosition,
      data: { label: type },
    };

    setNodes((nds) => [...nds, newNode]);
  };

  // Save workflow including the templateName (workflowName)
  const saveWorkflow = async () => {
    // Use the existing workflowId or generate a new one.
    const idToUse = workflowId || `${Date.now()}`;
    // Include templateName (workflowName) in the payload.
    const workflowData = { id: idToUse, templateName: workflowName, nodes, edges };

    // Save locally as a fallback.
    localStorage.setItem(WORKFLOW_STORAGE_KEY, JSON.stringify(workflowData));

    try {
      const response = await fetch("http://127.0.0.1:5000/save_workflow", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(workflowData),
      });

      if (response.ok) {
        alert(`Workflow saved successfully! ID: ${idToUse}`);
        // If this is a new workflow, navigate to a URL with the new workflowId.
        if (!workflowId) {
          navigate(`/workflow/${idToUse}`);
        }
      } else {
        alert("Failed to save workflow on backend.");
      }
    } catch (error) {
      console.error("Error saving workflow:", error);
      alert("Failed to save workflow.");
    }
  };

  // Execute the workflow by sending data to the backend.
  const executeWorkflow = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/execute_workflow/${workflowId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: workflowId || "new-workflow", nodes, edges }),
      });
      const result = await response.json();
      console.log("Execution Log:", result.log);
      alert("Workflow executed! Check console for logs.");
    } catch (error) {
      console.error("Error executing workflow:", error);
      alert("Execution failed.");
    }
  };

  if (loading) return <p>Loading workflow...</p>;

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-grow" onDragOver={onDragOver} onDrop={onDrop}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          onConnect={onConnect}
          fitView
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
        >
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
      <aside className="p-6 w-1/4 bg-gray-100 border-r shadow-md">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          {workflowName || "Save Workflow Blocks"}
        </h2>
        <button onClick={saveWorkflow} className="p-2 m-2 bg-blue-500 text-white rounded">
          Save Workflow
        </button>
        <button onClick={executeWorkflow} className="p-2 m-2 bg-green-500 text-white rounded">
          Run Workflow
        </button>
        <h2 className="text-lg font-bold">Node Details</h2>
      {selectedNode ? (
        <div className="mt-2">
          <p className="text-gray-700 font-semibold">
            Selected: {selectedNode.data.label}
          </p>

          {selectedNode.data.label === "Send Email" && (
            <div className="mt-2">
              <label className="block text-sm font-medium text-gray-700">
                Email ID:
              </label>
              <input
                type="email"
                // value={selectedNode.data.email || ""}
                onChange={(e) => handleInputChange(e, "email")}
                className="w-full px-2 py-1 border rounded mt-1"
                placeholder="Enter email..."
              />

              <label className="block text-sm font-medium text-gray-700 mt-2">
                Subject:
              </label>
              <input
                type="text"
                // value={selectedNode.data.subject || ""}
                onChange={(e) => handleInputChange(e, "subject")}
                className="w-full px-2 py-1 border rounded mt-1"
                placeholder="Enter subject..."
              />

              <label className="block text-sm font-medium text-gray-700 mt-2">
                Body:
              </label>
              <textarea
                // value={selectedNode.data.body || ""}
                onChange={(e) => handleInputChange(e, "body")}
                className="w-full px-2 py-1 border rounded mt-1"
                rows="4"
                placeholder="Enter email body..."
              />
            </div>
          )}
        </div>
      ) : (
        <p className="text-gray-500 mt-2">No node selected.</p>
      )}
      </aside>
    </div>
  );
};

const WorkflowBuilder = () => (
  <ReactFlowProvider>
    <WorkflowBuilderContent />
  </ReactFlowProvider>
);

export default WorkflowBuilder;

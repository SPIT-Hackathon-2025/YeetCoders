import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const Templates = () => {
  const [templates, setTemplates] = useState([]);
  const [workflowName, setWorkflowName] = useState(""); // For new workflow name input
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Fetch all workflows from the backend
  const fetchTemplates = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://127.0.0.1:5000/get_workflows");
      if (!response.ok) {
        throw new Error("Failed to fetch workflows");
      }
      const data = await response.json();
      setTemplates(data);
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTemplates();
  }, []);

  // Create a new workflow with a unique ID
  const handleCreateWorkflow = async () => {
    if (!workflowName.trim()) {
      alert("Please enter a workflow name.");
      return;
    }
    const workflowId = `wf-${Date.now()}`;

    const initialNodes = [
      {
        id:"1",
        type:"input",
        data: { label:"Start" },
        position: { x:250,y:5},
      },
    ];

    const newWorkflow = {
      id: workflowId,
      templateName: workflowName,
      nodes: initialNodes,
      edges: [],
    };

    try {
      const response = await fetch("http://127.0.0.1:5000/save_workflow", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newWorkflow),
      });

      if (response.ok) {
        setTemplates((prev) => [...prev, newWorkflow]);
        setWorkflowName("");
      } else {
        alert("Failed to create workflow.");
      }
    } catch (error) {
      console.error("Error saving workflow:", error);
      alert("Failed to create workflow.");
    }
  };

  // Delete a workflow by its ID
  const handleDeleteTemplate = async (templateId) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/delete_workflow/${templateId}`, {
        method: "DELETE",
      });
      if (!response.ok) {
        throw new Error("Failed to delete workflow");
      }
      setTemplates((prev) =>
        prev.filter((template) => template.id !== templateId)
      );
    } catch (err) {
      console.error(err);
      setError(err.message);
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-4">Saved Workflows</h1>

      {error && <p className="text-red-500 mb-4">{error}</p>}

      {/* Form for creating a new workflow */}
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={workflowName}
          onChange={(e) => setWorkflowName(e.target.value)}
          placeholder="Enter workflow name"
          className="border px-2 py-1 rounded"
        />
        <button
          onClick={handleCreateWorkflow}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Create Workflow
        </button>
      </div>

      {loading ? (
        <p className="text-gray-600">Loading workflows...</p>
      ) : templates.length === 0 ? (
        <p className="text-gray-500">No workflows saved yet.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {templates.map((template) => (
            <div
              key={template.id}
              className="relative border p-4 rounded shadow hover:shadow-md transition-shadow duration-200"
            >
              <h2 className="text-xl font-semibold text-gray-800">
                {template.templateName || "Unnamed Workflow"}
              </h2>

              <button
                onClick={() => navigate(`/workflow/${template.id}`)}
                className="mt-2 px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
              >
                Edit Workflow
              </button>

              <button
                onClick={() => handleDeleteTemplate(template.id)}
                className="absolute top-2 right-2 text-sm text-white bg-red-500 px-2 py-1 rounded hover:bg-red-600 transition-colors duration-200"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Templates;

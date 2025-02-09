import React from "react";

const WorkflowCanvas = ({ workflow }) => {
  return (
    <div className="min-h-[200px] bg-gray-50 p-4 border-dashed border-2 border-gray-300 rounded">
      {workflow.length === 0 ? (
        <p className="text-gray-400">Drag and drop blocks here</p>
      ) : (
        workflow.map((block) => (
          <div key={block.id} className="p-2 bg-green-500 text-white rounded mb-2">
            {block.label}
          </div>
        ))
      )}
    </div>
  );
};

export default WorkflowCanvas;

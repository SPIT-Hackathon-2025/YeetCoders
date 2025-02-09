import React from "react";

const Sidebar = () => {
  const onDragStart = (event, type) => {
    event.dataTransfer.setData("application/reactflow", type);
    event.dataTransfer.effectAllowed = "move";
  };

  const blocks = [
    { label: "Send Email", color: "bg-blue-500" },
    { label: "Receive Email", color: "bg-green-500" },
    { label: "Download attachments", color: "bg-orange-500"},
    { label: "If Condition", color: "bg-yellow-500" },
    { label: "Upload File", color: "bg-purple-500" },
    { label: "Read Spreadsheet", color: "bg-red-500" },
    { label: "Create Calender" , color:"bg-cyan-500"},
    { label: "Slack Notification", color: "bg-indigo-500" },
  ];

  return (
    <aside className="p-6 w-1/4 bg-gray-100 border-r shadow-md">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Workflow Blocks</h2>
      <div className="space-y-3">
        {blocks.map((block, index) => (
          <div
            key={index}
            className={`p-3 text-white text-center font-medium rounded-lg shadow-md cursor-pointer transition-all duration-200 hover:scale-105 hover:shadow-lg ${block.color}`}
            draggable
            onDragStart={(event) => onDragStart(event, block.label)}
          >
            {block.label}
          </div>
        ))}
      </div>
    </aside>
  );
};

export default Sidebar;
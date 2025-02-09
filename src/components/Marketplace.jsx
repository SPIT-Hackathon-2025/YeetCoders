import React from "react";
import { useNavigate } from "react-router-dom";

const Marketplace = () => {
  const navigate = useNavigate();

  // Static examples for the marketplace with prices in INR
  const marketplaceExamples = [
    {
      id: "wf-1739070924853",
      templateName: "Email to Drive Automation",
      description:
        "Automatically downloads attachments from Gmail and uploads them to Google Drive.",
      price: 799, // Price in INR
      seller: "alice@example.com",
    },
    {
      id: "2",
      templateName: "Invoice Processing Workflow",
      description:
        "Extracts invoice data from incoming emails and stores it in a spreadsheet.",
      price: 1199, // Price in INR
      seller: "bob@example.com",
    },
    {
      id: "3",
      templateName: "Social Media Monitor",
      description:
        "Monitors social media emails and compiles engagement metrics into a report.",
      price: 599, // Price in INR
      seller: "charlie@example.com",
    },
    {
      id: "4",
      templateName: "Customer Support Ticketing",
      description:
        "Converts incoming emails to support tickets and automatically logs responses.",
      price: 999, // Price in INR
      seller: "diana@example.com",
    },
  ];

  return (
    <div className="max-w-7xl mx-auto p-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-4">Workflow Marketplace</h1>
      <p className="mb-6 text-gray-600">
        Explore custom workflows shared by the community. Buy, sell, or share your own workflows to empower your business.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {marketplaceExamples.map((template) => (
          <div
            key={template.id}
            className="border p-4 rounded shadow hover:shadow-md transition-shadow duration-200"
          >
            <h2 className="text-xl font-semibold text-gray-800 mb-2">
              {template.templateName}
            </h2>
            <p className="text-gray-600 mb-2">{template.description}</p>
            <p className="text-indigo-600 font-bold mb-2">
              Price: ₹{template.price}
            </p>
            <p className="text-gray-500 text-sm mb-2">Seller: {template.seller}</p>
            <button
              onClick={() => navigate(`/workflow/${template.id}`)}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              View Details
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Marketplace;

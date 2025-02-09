import React from "react";

const features = [
  {
    title: "Drag & Drop Workflow Builder",
    description:
      "The heart of the platform is its intuitive drag-and-drop interface, allowing users to easily create automated workflows. With a visual editor, users can drag pre-built action blocks (like sending emails, uploading files, or reading data from spreadsheets) and trigger blocks (such as receiving a new email or clicking a button) into place. This interface ensures that even users with no technical background can set up complex workflows. Additionally, the platform supports conditional logic, enabling the use of if-else conditions, loops, and branching paths to build more sophisticated automations."
  },
  {
    title: "Multi-App Integrations",
    description:
      "The platform supports integrations with a wide range of popular apps, including Google Suite (Gmail, Google Drive, Calendar), communication tools like Slack and Microsoft Teams, project management platforms such as Trello and Notion, and databases like Airtable and Firebase. By connecting multiple apps, users can automate workflows between them. It also allows custom API integrations so users can extend its functionality by linking additional services or internal tools."
  },
  {
    title: "Multi-Step Triggers & Actions",
    description:
      "Workflows aren’t limited to a single action. The platform supports multi-step triggers and actions, enabling users to design intricate workflows that execute sequentially or in parallel. For example, a user can set up a trigger like 'When a new email arrives,' followed by actions like 'Download attachment,' 'Upload to Google Drive,' and 'Notify via Slack.' These workflows execute in real time, ensuring immediate actions when conditions are met and increasing efficiency."
  },
  {
    title: "Pre-Made Templates & Marketplace",
    description:
      "The platform offers ready-made templates that allow users to automate common tasks with a single click, such as saving Gmail attachments to Google Drive, syncing Notion pages with Google Calendar, or scheduling social media posts. Additionally, users can explore the template marketplace, where they can share, buy, or sell custom workflows, fostering a community-driven ecosystem where everyone can find workflows that suit their needs."
  }
];

const Features = () => {
  return (
    <div className="bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-4xl font-bold text-gray-800 text-center mb-8">Key Features</h1>
        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white p-6 rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300"
            >
              <h2 className="text-xl font-semibold text-indigo-600 mb-2">
                {feature.title}
              </h2>
              <p className="text-gray-600 text-sm">{feature.description}</p>
            </div>
          ))}
        </div>
        <div className="mt-12 text-center text-gray-500">
          SPIT HACKATHON 2025 • WEB DEVELOPMENT
        </div>
      </div>
    </div>
  );
};

export default Features;

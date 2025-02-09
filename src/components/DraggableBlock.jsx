import React from "react";
import { useDraggable } from "@dnd-kit/core";

const DraggableBlock = ({ block }) => {
  const { attributes, listeners, setNodeRef, transform } = useDraggable({ id: block.id });

  const style = {
    transform: transform ? `translate(${transform.x}px, ${transform.y}px)` : undefined,
  };

  return (
    <div
      ref={setNodeRef}
      {...listeners}
      {...attributes}
      className="p-2 bg-blue-500 text-white rounded cursor-pointer mb-2"
      style={style}
    >
      {block.label}
    </div>
  );
};

export default DraggableBlock;

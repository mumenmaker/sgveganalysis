import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { MapPin } from 'lucide-react';

const DraggableLegend = () => {
  const [position, setPosition] = useState({ x: 16, y: 16 }); // Default top-right position
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const legendRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({
      x: e.clientX - position.x,
      y: e.clientY - position.y,
    });
    e.preventDefault();
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging) return;

    const newX = e.clientX - dragStart.x;
    const newY = e.clientY - dragStart.y;

    // Constrain to viewport bounds
    const maxX = window.innerWidth - (legendRef.current?.offsetWidth || 256);
    const maxY = window.innerHeight - (legendRef.current?.offsetHeight || 200);

    setPosition({
      x: Math.max(0, Math.min(newX, maxX)),
      y: Math.max(0, Math.min(newY, maxY)),
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, dragStart]);

  return (
    <div
      ref={legendRef}
      className="absolute z-[1000] hidden sm:block"
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
        cursor: isDragging ? 'grabbing' : 'grab',
      }}
    >
      <Card className="w-64 bg-gray-700/70 border-gray-600/50 shadow-lg select-none">
        <CardHeader 
          className="pb-2 cursor-move"
          onMouseDown={handleMouseDown}
        >
          <CardTitle className="text-sm flex items-center space-x-2 text-white">
            <MapPin className="h-4 w-4 text-green-400" />
            <span>Legend</span>
            <span className="text-xs text-gray-400 ml-auto">⋮⋮</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-xs text-gray-200">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span>Vegan Restaurants</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-orange-500"></div>
            <span>Vegetarian Restaurants</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-purple-500"></div>
            <span>Has Veg Options</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <span>Other Restaurants</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DraggableLegend;

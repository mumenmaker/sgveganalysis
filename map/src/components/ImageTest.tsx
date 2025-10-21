import React, { useState } from 'react';

interface ImageTestProps {
  imageUrl: string;
  restaurantName: string;
}

const ImageTest: React.FC<ImageTestProps> = ({ imageUrl, restaurantName }) => {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');

  const handleImageLoad = () => {
    setStatus('success');
  };

  const handleImageError = () => {
    setStatus('error');
  };

  return (
    <div className="border p-4 m-2">
      <h3 className="font-bold">Image Test for {restaurantName}</h3>
      <p className="text-sm text-gray-600 mb-2">URL: {imageUrl}</p>
      
      <div className="w-32 h-32 border border-gray-300">
        <img
          src={imageUrl}
          alt={`${restaurantName} test`}
          className="w-full h-full object-cover"
          onLoad={handleImageLoad}
          onError={handleImageError}
        />
      </div>
      
      <div className="mt-2">
        Status: 
        <span className={`ml-2 px-2 py-1 rounded text-sm ${
          status === 'loading' ? 'bg-yellow-100 text-yellow-800' :
          status === 'success' ? 'bg-green-100 text-green-800' :
          'bg-red-100 text-red-800'
        }`}>
          {status}
        </span>
      </div>
      
      <button 
        onClick={() => window.open(imageUrl, '_blank')}
        className="mt-2 px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
      >
        Open in New Tab
      </button>
    </div>
  );
};

export default ImageTest;

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [location, setLocation] = useState('');
  const [date, setDate] = useState('');
  const [itineraries, setItineraries] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchItineraries();
  }, []);

  const fetchItineraries = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/itinerary');
      setItineraries(response.data);
    } catch (err) {
      setError('Failed to fetch itineraries');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await axios.post('http://localhost:5000/api/itinerary', {
        location,
        date,
      });
      setItineraries([...itineraries, response.data]);
      setLocation('');
      setDate('');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to add itinerary');
    }
  };

  return (
    <div className='bg-[url("/rome.jpg")] bg-cover min-h-screen'>
      <div className="max-w-2xl mx-auto p-4">
        <h1 className="text-white text-3xl font-bold text-center mb-6">Travel Itinerary Planner</h1>
        <div className="bg-white/80 p-6 rounded-lg shadow-md mb-6">
          <h2 className="text-[24px] text-center font-semibold mb-4">Add Destination</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Location</label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm p-2"
                placeholder="e.g., Paris, France"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Date</label>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm p-2"
              />
            </div>
            {error && <p className="text-red-500">{error}</p>}
            <button
              onClick={handleSubmit}
              className="w-full bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600"
            >
              Add to Itinerary
            </button>
          </div>
        </div>
        <div className='flex flex-col justify-center items-center'>
          <div className="bg-white/80 min-w-3xl p-6 rounded-lg shadow-md">
            <h2 className="text-[28px] text-center font-semibold mb-4">Your Itinerary</h2>
            {itineraries.length === 0 ? (
              <p className="text-gray-500">No destinations added yet.</p>
            ) : (
              <ul className="space-y-4">
                {itineraries.map((item, index) => (
                  <li key={index} className="border-b pb-4">
                    <div className='flex flex-col justify-center items-center'>
                      {item.image_url ? (
                        <img
                          src={item.image_url}
                          alt={item.location}
                          className="w-full h-48 object-cover rounded-md mb-4"
                        />
                      ) : (
                        <p className="text-gray-500 mb-4">No image available</p>
                      )}
                      <h3 className="text-lg font-medium">{item.location}</h3>
                      <p className="text-gray-600">{item.date}</p>
                      <p className="text-gray-700 mt-2">{item.description}</p>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import ScanDetails from './pages/ScanDetails';

function App() {
    return (
        <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/scans/:id" element={<ScanDetails />} />
        </Routes>
    );
}

export default App;

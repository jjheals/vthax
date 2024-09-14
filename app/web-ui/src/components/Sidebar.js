// src/components/Sidebar.js

import React, { useEffect, useState } from 'react';
import Hamburger from './Hamburger';
import { options } from '../config.js';
import L from 'leaflet';
import forge from 'node-forge';

import '../css/Sidebar.css'; 


const Sidebar = ({ mapInstance }) => {
    const [isSidebarOpen, setIsOpen] = useState(false);
    const [inputParams, setInputParams] = useState({
        'vehicles': [],
        'strategies': [],
        'objectives': []
    });

    const [vehiclesParams, setVehicleParams] = useState([]);
    const [strategyParams, setStrategyParams] = useState([]);
    const [objectiveParams, setObjectiveParams] = useState([]);
    const [possiblePaths, setPossiblePaths] = useState([]);
    const [pathLayers, setPathLayers] = useState([]);

    const colors = [
        'red',
        'blue',
        'green',
        'orange',
        'purple',
        'yellow',
        'grey'
    ]


    /**
     * @constant toggleSidebar event handler for toggling hiding/showing the sidebar.
     * @returns { null }
     */
    const toggleSidebar = () => {
        setIsOpen(!isSidebarOpen);
    };


    /**
     * @function displayPathsOnMap clears the paths currently shown on the map, and displays the new given paths 
     * @param { Array<Array<Number, Number>>} paths a list of paths as lists of points (tuples/arrays)
     */
    function displayPathsOnMap(paths) { 

        // Clear previous path layers from the map
        pathLayers.forEach(layer => mapInstance.removeLayer(layer));
        
        // Create new path layers and store references
        const newPathLayers = paths.map((pathCoordinates, index) => {

            // Create the path line
            const path = L.polyline(pathCoordinates, { color: colors[index % colors.length] });

            // Add a popup that appears on hover of the line
            path.on('mouseover', (e) => {
                const polyline = e.target;
                const latlngs = polyline.getLatLngs();
                const pathLength = latlngs.length > 1 
                    ? `Length: ${(L.latLng(latlngs[0]).distanceTo(L.latLng(latlngs[latlngs.length - 1])).toFixed(2)) / 1000} km`
                    : 'Single point';
    
                polyline.bindTooltip(`<b>Path ${index + 1}</b><br>${pathLength}`, {
                    permanent: false,
                    direction: 'top'
                }).openTooltip();
            });

            // Close tooltip on mouseout
            path.on('mouseout', (e) => {
                path.closeTooltip();
            });

            // Add the path to the map
            path.addTo(mapInstance);
            return path;
        });

        // Update state with new path layers
        setPathLayers(newPathLayers);
    }


    /**
     * @constant submitForm event handler for submitting the user input params form from the sidebar 
     * @param { Event } e 
     */
    const submitForm = async (e) => { 
        e.preventDefault();
    
        const formData = new FormData(e.target);

        try {
            // Send the FormData object to the API
            const response = await fetch('http://localhost:8000/submit-form', {
                method: 'POST',
                body: formData,
            });
    
            // Check if the request was successful
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
    
            // Get the response data
            const responseData = await response.json();
            console.log('Response:', responseData);

            setPossiblePaths(responseData.paths);
    
        } catch (error) {
            console.error('Error:', error);
        }
    }


    /**
     * @function getInputParamsData retrieves the data from the API on init of the page.
     * @returns { null }
     */
    async function getInputParamsData() { 
        // Get the data from the API 
        const response = await fetch('http://localhost:8000/get-input-params', options);
        const responseJson = await response.json();
        return responseJson;
    }


    // useEffect() => inits the page on load
    useEffect(() => { 

        // Async helper to fetch the input params using getInputParamsData
        async function fetchInputParams() {
            try {
                const data = (await getInputParamsData()).data;
                setInputParams(data);
            } catch (error) {
                console.error("Error fetching input params:", error);
            }
        }

        // Initial call of fetchInputParams
        fetchInputParams();
    }, []);


    // useEffect() => updates the map if the possible paths variable is updated
    useEffect(() => { 
        displayPathsOnMap(possiblePaths);
    }, [possiblePaths, mapInstance]);


    // useEffect() => sets the parameters for user inputs when the API responds with the data 
    useEffect(() => {
        try { setVehicleParams(inputParams.vehicles); }
        catch { console.log('not given vehicles'); } 

        try { setStrategyParams(inputParams.strategies); }
        catch { console.log('not given strategies'); } 

        try { setObjectiveParams(inputParams.objectives); }
        catch { console.log('not given objectives'); } 

    }, [inputParams]);


    return (
        <div className='sidebar-container'>
            <Hamburger onClickFunc={toggleSidebar} className={isSidebarOpen ? 'open' : '' }/>

            <div className={`sidebar ${isSidebarOpen ? 'open' : 'closed'}`}>
            <h2 className='sidebar-title'>User Input Parameters</h2>
                <form className="sidebar-content" onSubmit={submitForm}>
                    
                    {/* Available vehicles section */}
                    <div className='sidebar-section'>
                        <h3 className='sidebar-section-header'>Available Vehicles</h3>
                        {
                            vehiclesParams.length > 0 ? (
                                vehiclesParams.map(vehicle => (
                                    <div className='input-row' key={vehicle['vehicle-id']}>   
                                        <input 
                                            type='checkbox' 
                                            className='vehicle-input-checkbox' 
                                            id={vehicle['vehicle-id']}
                                            name={vehicle['vehicle-id']}
                                        />
                                        <label>
                                            {vehicle['vehicle-name']}
                                        </label>
                                        <div className='info-icon'>
                                            i
                                            <div className='info-tooltip'>
                                                {vehicle['vehicle-description']}
                                            </div>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <p>No vehicles available</p>
                            )
                        }
                    </div>

                    {/* Location section */}
                    <div className='sidebar-section'>
                        <h3 className='sidebar-section-header'>Location Information</h3>
                        <div className='input-row'>
                            <label>Starting Location</label>
                            <input type='text' className='loc-input' id='start-lat-input' name='start-lat' placeholder='lat'></input>
                            <input type='text' className='loc-input' id='start-long-input' name='start-long' placeholder='lon'></input>
                        </div>
                        <div className='input-row'>
                            <label>Objective Location</label>
                            <input type='text' className='loc-input' id='end-lat-input' name='end-lat'  placeholder='lat'></input>
                            <input type='text' className='loc-input' id='end-long-input' name='end-lon' placeholder='lon'></input>
                        </div>
                    </div>

                    {/* Logistics section */}
                    <div className='sidebar-section'>
                        <h3 className='sidebar-section-header'>Logistical Information</h3>

                        <div className='input-row'><label>Total Personnel</label><input type='number' name='personnel' id='personnel-input'></input></div>
                        <div className='input-row'><label>Target time on OBJ (hrs)</label><input type='number' name='target-time-on-obj' id='time-on-obj-input'></input></div>
                        
                        <div className='input-row'>
                            <label>Strategy</label>
                            <select name='strategy' id='strategy-input'>
                                {
                                    strategyParams.length > 0 ? (
                                        strategyParams.map(strategy => (
                                            <option name={strategy['strategy-id']} key={strategy['strategy-id']} value={strategy['strategy-id']}>{strategy['strategy-name']}</option>
                                        ))
                                    ) : (
                                        <option></option>
                                    )
                                }
                            </select>
                        </div>
                    
                        <div className='input-row'>
                            <label>Objective</label>
                            <select name='objective' id='objective-input'>
                                {
                                    objectiveParams.map(obj => (
                                        <option name={obj['objective-id']} key={obj['objective-id']} value={obj['objective-id']}>{obj['objective-name']}</option>
                                    ))
                                }
                            </select>
                        </div>
                    </div>

                    {/* Intelligence Section */}
                    <div className='sidebar-section'>
                        <h3 className='sidebar-section-header'>Known Intelligence</h3>

                        <div className='input-row'>
                            <label>Expected Resistance</label>
                            <select name='resistance' id='resistance-input'>
                                <option name='none' key='none' value='none'>None</option>
                                <option name='low' key='low' value='low'>Low</option>
                                <option name='med' key='med' value='med'>Medium</option>
                                <option name='high' key='high' value='high'>High</option>
                            </select>
                        </div>
                    </div>
                    
                    {/* ChatGPT config section */}
                    <div className='sidebar-section'>
                        <h3 className='sidebar-section-header'>OpenAI Configuration</h3>
                        <p className='sidebar-subdesc'>
                            This application uses <a href='https://openai.com'>OpenAI's</a> ChatGPT model for generating contextual mission plans and requires an 
                            OpenAI API key. This application is not sponsored by or in direct cooperation with OpenAI. Your API key is not stored on the server and is discarded after use.
                            If you do not supply an API key, then the application will still generate a mission plan but will lack an AI generated summary of the recommendations.
                        </p>
                   
                        <div className='input-row'>
                            <input name='openai-api-key' id='openai-api-key-input' placeholder='<your-openai-api-key>'></input>
                        </div>

                        <div className='input-row'>
                            <select name='openai-model' id='openai-model-input'>
                                <option name='select-model'>Select a model</option>
                                <option name='gpt-4' value='gpt-4'>GPT-4</option>
                                <option name='gpt-3.5-turbo' value='gpt-3.5-turbo'>GPT-3.5-Turbo</option>
                            </select>
                        </div>
                    </div>

                    {/* Submit button */}
                    <button type='submit'>Generate</button>
                </form>
            </div>
        </div>
    );
};

export default Sidebar;

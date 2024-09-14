import React, { useEffect, useState } from 'react';
import Hamburger from './Hamburger';
import { options } from '../config.js';

import '../css/Sidebar.css'; 

const Sidebar = () => {
    const [isSidebarOpen, setIsOpen] = useState(false);
    const [inputParams, setInputParams] = useState({
        'vehicles': [],
        'strategies': [],
        'objectives': []
    });

    const [vehiclesParams, setVehicleParams] = useState([]);
    const [strategyParams, setStrategyParams] = useState([]);
    const [objectiveParams, setObjectiveParams] = useState([]);

    /**
     * @constant toggleSidebar event handler for toggling hiding/showing the sidebar.
     * @returns { null }
     */
    const toggleSidebar = () => {
        setIsOpen(!isSidebarOpen);
    };


    /**
     * @constant submitForm event handler for submitting the user input params form from the sidebar 
     * @param { Event } e 
     */
    const submitForm = async (e) => { 
        e.preventDefault();

        const formData = new FormData(e.target);

        // Convert FormData to a plain object (for easier logging)
        const dataObject = {};
        formData.forEach((value, key) => {
            dataObject[key] = value;
        });

        console.log('Submitting form data:');
        console.log(dataObject); // Log the form data

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

                <form className="sidebar-content" onSubmit={submitForm}>
                    <h2 className='sidebar-title'>User Input Parameters</h2>

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
                            <input type='number' className='loc-input' id='start-lat-input' name='start-lat' placeholder='lat'></input>
                            <input type='number' className='loc-input' id='start-long-input' name='start-long' placeholder='lon'></input>
                        </div>
                        <div className='input-row'>
                            <label>Objective Location</label>
                            <input type='number' className='loc-input' id='end-lat-input' name='end-lat'  placeholder='lat'></input>
                            <input type='number' className='loc-input' id='end-long-input' name='end-lon' placeholder='lon'></input>
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
                    
                    {/* Submit button */}
                    <button type='submit'>Generate</button>
                </form>
            </div>
        </div>
    );
};

export default Sidebar;

import React, { useEffect, useState } from 'react';
import Hamburger from './Hamburger';
import { options } from '../config.js';

import '../css/Sidebar.css'; 

const Sidebar = () => {
    const [isSidebarOpen, setIsOpen] = useState(false);
    const [inputParams, setInputParams] = useState({
        'vehicles': []
    });

    const [vehiclesParams, setVehicleParams] = useState([]);
    const [strategyParams, setStrategyParams] = useState([]);


    const toggleSidebar = () => {
        setIsOpen(!isSidebarOpen);
    };


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
     * @function getData retrieves the data from the API on init of the page.
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
                            <input type='number' className='loc-input' id='end-long-input' name='end-lat' placeholder='lon'></input>
                        </div>
                    </div>

                    {/* Logistics section */}
                    <div className='sidebar-section'>
                        <div className='input-row'>
                            <label>Total Personnel</label><input type='number' name='personnel' id='personnel-input'></input>
                        </div>
                        <div className='input-row'>
                            <label>Target time on OBJ (hrs)</label><input type='number' name='target-time-on-obj' id='time-on-obj-input'></input>
                        </div>
                        <div className='input-row'>
                            <label>Strategy</label>
                            <select id='strategy-input'>
                                {

                                }
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

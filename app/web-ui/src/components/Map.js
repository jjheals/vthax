
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { useEffect, useState } from 'react';
import L from 'leaflet';

import '../css/Map.css';
import 'leaflet/dist/leaflet.css';


const Map = ({ data }) => {

    const maxZoom = 20;
    const minZoom = 3;
    const startingLoc = [0, 0] 
    const bounds = [[-90, -180], [90, 180]]; 
    var map = null;


    /**
     * Initializes a leaflet map in the given container.
     * 
     * @param { String } container the ID of the container element
     * @returns { L.Map } a leaflet map
     */
    function init_map(container) { 

        // Create the map
        const map = L.map(container).setView(
            startingLoc,  // Starting location
            minZoom       // Use min zoom for the starting zoom
        );
        
        // Add a default basemap tile layer 
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: maxZoom,
            minZoom: minZoom,
            attribution: '&copy; OpenStreetMap contributors',
            noWrap: true
        }).addTo(map);

        // Add the max bounds for the map if specified
        map.setMaxBounds(bounds);

        // Remove the default zoom control
        map.zoomControl.remove();

        // Create a new zoom control with custom options
        const zoomControl = L.control.zoom({
            position: 'topright' // Change position to topright
        });

        // Add the new zoom control to the map
        zoomControl.addTo(map);
        
        // Return the map
        return map
    }

    /**
     * @function displayDataOnMap displays the given data on the map. NOTE: assumes that the data is in the format
     * as returned by fetchCsvData, and that the columns all exist (but nulls are accepted). 
     * 
     * @param { Array<Object> } data the data as returned by fetchCsvData
     * @param { any } map a Leaflet map object to render the data on
     * @returns { Array<CustomMarker> } an array containing all of the custom marker objs
     */
    function displayDataOnMap(data, map) {

        console.log('display data on map given data');
        console.log(data);

        var allMarkers = [];

        // Iterate over the data 
        let i = 0;
        data.forEach(row => {

            // Extract the latitude and longitude from this row 
            const latitude = parseFloat(row.latitude);
            const longitude = parseFloat(row.longitude);

            // TO DO: logic to pick the correct color for this marker 
            // DO SOMETHING 
            const markerColor = 'red';

            // Create custom icon
            const customIcon = L.divIcon({
                className: 'marker',
                html: `<div style="
                    background-color: ${markerColor};
                    width: 20px; height: 20px;
                    border-radius: 50%;
                    border: 2px solid white;
                    box-shadow: 0 0 5px rgba(0,0,0,0.5);
                "></div>`,
                iconSize: [20, 20], 
            });

            // Create a marker for this data point 
            L.marker([latitude, longitude], { icon: customIcon })
                .addTo(map)
                .bindPopup('<div className="popup">Popup</div>')
                .openPopup();

            i++;
        });

        // Return the populated array
        return allMarkers;
    }


    useEffect(() => { 

        // Initialize the map
        if(!map) map = init_map('map');
        
        // Add markers 
        displayDataOnMap(data, map);
    }, []);
    
    

    return (
        <div className='map-container'>
            <div id='map' style={{ width: '100%' }}></div>
        </div>
    )
}


export default Map;
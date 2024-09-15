// src/components/Map.js

import { gridLayer } from 'react-leaflet';
import { useEffect, useState } from 'react';
import L from 'leaflet';
import { basemaps } from '../basemaps';

import '../css/Map.css';
import 'leaflet/dist/leaflet.css';


const Map = ({ onMapReady }) => {
    const [mapInstance, setMapInstance] = useState(null);
    const [currentBasemap, setCurrentBasemap] = useState('CartoDark'); // Default basemap

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
        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png', {
            maxZoom: maxZoom,
            minZoom: minZoom,
            attribution: '&copy; OpenStreetMap contributors &copy; CartoDB',
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
     * @function updateBasemap updates the currently displayed basemap on the map
     * @param { String } newBasemap 
     */
    function updateBasemap(newBasemap) {
        if (mapInstance) {
            // Remove the current basemap
            mapInstance.eachLayer(layer => {
                if (layer instanceof L.TileLayer) {
                    mapInstance.removeLayer(layer);
                }
            });
            // Add the new basemap
            L.tileLayer(basemaps[newBasemap]['link'], {
                maxZoom: maxZoom,
                minZoom: minZoom,
                attribution: basemaps[newBasemap]['attribution'],
                noWrap: true
            }).addTo(mapInstance);
        }
        setCurrentBasemap(newBasemap);
    }


    useEffect(() => { 

        // Initialize the map
        if(!map) map = init_map('map');
        
        setMapInstance(map);
        if (onMapReady) onMapReady(map); // Notify parent component        
    }, []);
    
    

    return (
        <div className='map-container'>
            <div id='map' style={{ width: '100%' }}></div>
            <div className="basemap-selector">
                <select onChange={(e) => updateBasemap(e.target.value)} value={currentBasemap}>
                    {
                        Object.entries(basemaps).map(([mapName, info]) => (
                            <option value={mapName}>{info.prettyName}</option>
                        ))
                    }
                </select>
            </div>
        </div>
    )
}


export default Map;
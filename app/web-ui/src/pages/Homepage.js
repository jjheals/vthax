//src/pages/Homepage.js

import { useEffect, useState } from 'react';

import Sidebar from '../components/Sidebar.js';
import Map from '../components/Map.js';

const Homepage = () => {
    const [mapInstance, setMapInstance] = useState(null);

    return(
        <div className='homepage'> 
            <div className='header-bar'></div>

            <Sidebar mapInstance={mapInstance}/>
            <Map onMapReady={setMapInstance}/>
        </div>
    );
}


export default Homepage;
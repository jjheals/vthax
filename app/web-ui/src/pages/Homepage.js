
import { useEffect, useState } from 'react';

import Sidebar from '../components/Sidebar.js';
import Map from '../components/Map.js';

const Homepage = () => {
    return(
        <div className='homepage'> 
            <div className='header-bar'></div>

            <Sidebar />
            <Map data={{}}/>
        </div>
    );
}


export default Homepage;
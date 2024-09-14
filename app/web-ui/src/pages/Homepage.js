
import { useEffect, useState } from 'react';

import Sidebar from '../components/Sidebar.js';


const Homepage = () => {
    return(
        <div className='homepage'> 
            <div className='header-bar'></div>

            <Sidebar />
        </div>
    );
}


export default Homepage;
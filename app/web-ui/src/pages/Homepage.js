
import { useEffect } from 'react';
import { options } from '../config.js';


const Homepage = () => {

    /**
     * @function getData retrieves the data from the API on init of the page.
     * @returns { null }
     */
    async function getData() { 
        // Get the data from the API 
        fetch('http://localhost:8000/generate-plan', options);
    }

    // useEffect() => inits the page on load
    useEffect(() => { 
        getData();
    }, []);
    

    return(
        <div className='homepage'> 
            <p>Hello, world!</p>
        </div>
    );
}


export default Homepage;
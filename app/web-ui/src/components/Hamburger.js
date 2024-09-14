
import '../css/Hamburger.css';

const Hamburger = ({ onClickFunc, className }) => { 
    return (
        <div className={`hamburger ${className}`} id='hamburger' onClick={onClickFunc}>
            <span className='hamburger-component'></span>
            <span className='hamburger-component'></span>
            <span className='hamburger-component'></span>
        </div>
    )
}


export default Hamburger;
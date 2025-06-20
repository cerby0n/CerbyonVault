import { Link } from 'react-router-dom';
import spaceShip from "../assets/vector-rocket.png"

export default function NotFound() {
    return (
        <div className='min-h-screen flex flex-col items-center justify-center bg-gray-700/75 relative'>

        <h1 className="text-5xl font-bold mt-10 text-indigo-100 z-20">
          Oops! Looks like you’ve floated off course.
        </h1>
        <p className="text-xl mt-4 text-indigo-100 z-20">
          The page you’re looking for has disappeared into the vast universe.
        </p>
        <div className="absolute h-225 z-10" >
            <img src={spaceShip} alt="spaceship" className='w-50 object-scale-down'/>
        </div>
  
        <div className="mt-6 flex space-x-4 z-10">
          <Link
            to="/"
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-700 transition duration-300"
          >
            Return to Mission Control
          </Link>
        </div>
      </div>
    ); 
  }
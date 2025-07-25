import axios from "axios";
import React from "react";

// TODO: to envs
const baseURL = "http://0.0.0.0:8000/api/v1/hotels";

// TODO: start page, add other pages
function App() {
    const [hotels, setHotels] = React.useState(null);

    // TODO: getting of date_from: and date_to
    React.useEffect(() => {
        axios.get(baseURL, {params: {date_from: "2024-07-10", date_to: "2024-07-19"}})
            .then((response) => {
                setHotels(response.data.content);
        });
    }, []);
    return (
        <div>
            {hotels && hotels.map(hotel => {
                return <div>
                    <h1>{hotel.name}</h1>
                    <p>{hotel.location}</p>
                </div>
            })}
        </div>
    );
}

export default App;

import axios from "axios";
import React from "react";

const baseURL = "http://localhost:8010/api/v1/hotels";

function App() {
    const [hotels, setHotels] = React.useState(null);

    React.useEffect(() => {
        axios.get(baseURL, {params: {date_from: "2024-07-10", date_to: "2024-07-19"}})
            .then((response) => {
                setHotels(response.data);
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

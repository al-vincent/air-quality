"use strict";

// lat, lng, intensity for different types of emissions
const EMISSION_TYPES = JSON.parse(document.getElementById('geo-data').textContent)
// default values for drop-down menus
const DEFAULT_EMISSIONS = "CO"; 
const DEFAULT_ILLNESS = "asthma";

// ***************************************************************************************************
// Helper functions 
// ***************************************************************************************************
function getEmissionsValues(emissionsType){
    return EMISSION_TYPES.map( function(elem) {        
        return [elem["lat"], elem["lng"], elem[emissionsType]];
    });
}

// ***************************************************************************************************
// Main 
// ***************************************************************************************************
function main(){
    // Location functions
    function onLocationFound(pos) {
        const radius = pos.accuracy / 2;
        L.marker(pos.latlng)
            .bindPopup("You are within " + radius + " metres of this point").openPopup()
            .addTo(map);

        L.circle(pos.latlng, radius).addTo(map);
    }

    function onLocationError(e) {
        alert(e.message);
    }

	// create the map using the travelMap ID tag. Set the (lat, lon) render-centre, and initial zoom level
	let map = L.map("map", { zoom: 16 });
    // get the user's position
    map.locate({ setView: true});
    map.on('locationfound', onLocationFound);
    map.on('locationerror', onLocationError);

    let heat = null;
        	
	// get tiles from openstreetmap.org, add attribution etc. Add tiles to map.
	L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
			maxZoom: 18,
			subdomains: ['a','b','c']
			}).addTo(map);
    
    // add a series of points ot the map, with randomly-generated intensities
    heat = L.heatLayer(getEmissionsValues(DEFAULT_EMISSIONS), 
                            {radius: 15, blur: 5}).addTo(map); 
    console.log(heat);

    const emissionsList = document.getElementById('list-emissions');
    emissionsList.addEventListener("change", function(){
        const newEmissionsType = document.getElementById('list-emissions').value;
        // get the new intensities
        const newEmissions = getEmissionsValues(newEmissionsType);
        // remove the existing points from the map
        heat.remove();
        // plot the new points
        heat = L.heatLayer(newEmissions, {radius: 15, blur: 5}).addTo(map);
        console.log(heat);
        console.log("map updated");
    });
}

// run the script
main();
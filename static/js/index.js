"use strict";

console.log("Emissions data:")
console.log(JSON.parse(document.getElementById('geo-data').textContent));

// lat, lng, intensity for different types of emissions
const EMISSION_TYPES = JSON.parse(document.getElementById('geo-data').textContent)
const DEFAULT_EMISSIONS = "CO";
const DEFAULT_ILLNESS = "asthma";

function getEmissionsValues(emissionsType){
    return EMISSION_TYPES.map( function(elem) {        
        return [elem["lat"], elem["lng"], elem[emissionsType]];
    });
}

function main(){
	// create the map using the travelMap ID tag. Set the (lat, lon) render-centre, and initial zoom level
	let map = L.map("map", {
		center: [-37.9, 175.475], 
		zoom: 16
        });

    let heat = null;
        	
	// get tiles from openstreetmap.org, add attribution etc. Add tiles to map.
	L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
			maxZoom: 18,
			subdomains: ['a','b','c']
			}).addTo(map);
    
    // add a series of points ot the map, with randomly-generated intensities
    // console.log(getEmissionsValues(DEFAULT_EMISSIONS));
    heat = L.heatLayer(getEmissionsValues(DEFAULT_EMISSIONS), 
                            {radius: 15, blur: 5}).addTo(map); 
    console.log(heat);
    
    const emissionsList = document.getElementById('list-emissions');
    emissionsList.addEventListener("change", function(){
        const newEmissionsType = document.getElementById('list-emissions').value;
        console.log("New emissions type:");
        console.log(newEmissionsType);
        // get the new intensities (need to check via console!)
        const newEmissions = getEmissionsValues(newEmissionsType);
        console.log("New emissions values:");
        console.log(newEmissions);
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
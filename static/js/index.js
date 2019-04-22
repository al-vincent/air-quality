"use strict";

// lat, lng, intensity for different types of emissions
const EMISSION_LEVELS = JSON.parse(document.getElementById('geo-data-id').textContent);
const EMISSION_INFO = JSON.parse(document.getElementById('emissions-info-id').textContent);

// default values for drop-down menus
const DEFAULT_EMISSIONS = "Nitrogen Dioxide";
const DEFAULT_CODE = "NO2";
const DEFAULT_ILLNESS = "asthma";

// get bounding box for London
const MIN_LAT = 51.357, MAX_LAT = 51.669;
const MIN_LNG = -0.461, MAX_LNG = 0.206;

// ***************************************************************************************************
// Helper functions 
// ***************************************************************************************************
/**
 * @summary Filters the emissions data to show only the emissions levels for a single pollutant (e.g. 
 * ozone, sulphur dioxide, nitrogen dioxide etc.)
 * @param {*} emissionsType, 
 * @returns object, { max: float, the max that the 'value' parameter can take,
 *                    data: object array of form [{"lat": float, decimal latitude, 
 *                                                 "lng": float, decimal longitude,
 *                                                 "value": level of emissions measured at this point}] } 
 */
function getEmissionsValues(emissionsType){
    let newData = [];
    for(let i = 0; i < EMISSION_LEVELS.length; i++){
        if(EMISSION_LEVELS[i][emissionsType] !== null){
            newData.push({"lat": EMISSION_LEVELS[i]["Latitude"], 
                          "lng": EMISSION_LEVELS[i]["Longitude"], 
                          "value": EMISSION_LEVELS[i][emissionsType]});
        }
    }
    return { max: 1, data: newData };
}

function getEmissionsInfo(emissionsType){
    for(let i = 0; i < EMISSION_INFO.length; i++){
        if(EMISSION_INFO[i]['SpeciesName'] === emissionsType){
            return EMISSION_INFO[i];
        }
    }
    return null;
}

function changeEmissionsInfoElements(emissionInfo){
    document.getElementById('info-emissions').innerHTML = emissionInfo['SpeciesName'];
    document.getElementById('description-emissions').innerHTML = emissionInfo['Description'];
    document.getElementById('health-effect-emissions').innerHTML = emissionInfo['HealthEffect'];
    document.getElementById('link-emissions').innerHTML = emissionInfo['Link'];
}

// ***************************************************************************************************
// Main 
// ***************************************************************************************************
function main(){
    // ----------------------------------------------------------------------------------------------
    // Get user location, adjust map to show user loc or all of London
    // ----------------------------------------------------------------------------------------------
    let userLoc = {"latlng": null, "bounds": null};
    // console.log(userLoc); 

    /**
     * Callback function, fired if the user's location has successfully been acquired from their
     * device (i.e. via bulit-in GPS). Adds a marker to the map at the location with the marker size
     * indicating the accuracy of position info. 
     * @param {*} pos 
     */
    function onLocationFound(pos) {
        console.log("location found");
        const radius = pos.accuracy / 2;
        L.marker(pos.latlng)
            .bindPopup("You are within " + radius + " metres of this point").openPopup()
            .addTo(map);

        L.circle(pos.latlng, radius).addTo(map);
        userLoc = {"latlng": pos.latlng, "bounds": pos.bounds};
    }

    function onLocationError(e) {
        console.log("location NOT found");
        return e.message;
    }

    function isPointInLondon(latlng) {        
        if(latlng !== null) {
            if(MIN_LAT <= latlng[0]  && latlng[0] <= MAX_LAT) {
                if(MIN_LNG <= latlng[1]  && latlng[1] <= MAX_LNG) {
                    // the user's latlng is within greater London
                    return true;
                }
            }
        } else {
            return false; 
        }
    }   

	// get tiles from openstreetmap.org, add attribution etc. Add tiles to map.
	let baseLayer = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
			maxZoom: 18,
			subdomains: ['a','b','c']
			});
    
    // ----------------------------------------------------------------------------------------------
    // Generate heatmap
    // ----------------------------------------------------------------------------------------------
    // cfg is a heatmap.js config variable
    let cfg = {        
        "radius": 30,             // set the radius of the heatmap points (bit trial-and-error...)
        "maxOpacity": .7,         // sets how opaque (i.e. non-transparent) the heatmap points are
        "scaleRadius": false,     // scales point radius based on map zoom         
        "useLocalExtrema": false, // use *global* heatmap values at all times (i.e. max *always* 1)       
        latField: 'lat',          // fieldname used for latitude
        lngField: 'lng',          // fieldname used for longitude
        valueField: 'value'       // fieldname used for heat value
    };
    // create the heatmap layer
    let heatmapLayer = new HeatmapOverlay(cfg);

    // create the map using the 'map' ID tag, and add the two layers
    let map = L.map("map", { layers: [baseLayer, heatmapLayer]});
    
    // ----------------------------------------------------------------------------------------------
    // Get user location
    // ----------------------------------------------------------------------------------------------
    // try to get the user's position (*do not* centre the view on the user)
    map.locate({ setView: false });
    // set up callbacks based on whether user's location was correctly found
    map.on('locationfound', onLocationFound);
    map.on('locationerror', onLocationError);
    // if the user's location is available, get both the (lat, lng) coords and a bounding box.
    if(isPointInLondon(userLoc["latlng"])){
        map.fitBounds(userLoc["bounds"], maxZoom = 4);
    } else {
        // otherwise, set the box on central London
        map.fitBounds([
            [MIN_LAT, MIN_LNG],
            [MAX_LAT, MAX_LNG]
        ]);
    } 
    // initialise the heatmap with data from API
    document.getElementById('list-emissions').value = DEFAULT_CODE;
    heatmapLayer.setData(getEmissionsValues(DEFAULT_EMISSIONS));

    // change the text of the emissions elements to be about emission we're looking at
    changeEmissionsInfoElements(getEmissionsInfo(DEFAULT_EMISSIONS));

    // ----------------------------------------------------------------------------------------------
    // Add an event listener, to update the map when the list-emissions drop-down changes
    // ----------------------------------------------------------------------------------------------
    const emissionsList = document.getElementById('list-emissions');
    emissionsList.addEventListener("change", function(){
        // listen for a change in the emissions drop-down
        const newEmissionsType = document.getElementById('list-emissions').selectedOptions[0].text;
        
        // get the new emissions intensities
        heatmapLayer.setData(getEmissionsValues(newEmissionsType));
        console.log("map updated - change to " + newEmissionsType);

        // update the text of the emissions elements 
        changeEmissionsInfoElements(getEmissionsInfo(newEmissionsType));

    });
}

// run the script
main();
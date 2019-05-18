/** 
 * TODOs:
 * =====
 * 
 * LocalAuth onchange
 * ------------------
 * - add a mini-graph for LA-level (/ Group) emissions
 * - add info about each of the sites; what they collect, whether they're active etc.
 * - display mini-graphs for each site, on the emissions they've collected?
 * 
 * Display
 * -------
 * - Use heatmap for zoom > 10? [Check value]
 *      -- Alternative: average site values across a LocalAuth, and display as circles?
 * - For LocalAuths; display site values as numbers in circles (a few options for adding nums)
 *      -- Need to hide circles in other local auths, or set opacity = 0.1 or something
 *      -- Also need to use different colours for 'dead' sites
 *      -- When the map is resized (zoomed), change the size of the circlemarker <== may be ok?
 * */ 

"use strict";

// lat, lng, intensity for different types of emissions
const EMISSION_LEVELS = JSON.parse(document.getElementById('emissions-data-id').textContent);
console.log("EMISSION_LEVELS:");
console.log(EMISSION_LEVELS);
const EMISSION_INFO = JSON.parse(document.getElementById('emissions-info-id').textContent);
const LOCAL_AUTHORITIES = JSON.parse(document.getElementById('local-auths-id').textContent);
const SITES = JSON.parse(document.getElementById('sites-id').textContent);

// default values for drop-down menus
const DEFAULT_EMISSIONS = "Nitrogen Dioxide";
const DEFAULT_CODE = "NO2";
const DEFAULT_ILLNESS = "asthma";

// get bounding box for London
const MIN_LAT = 51.357, MAX_LAT = 51.669;
const MIN_LNG = -0.461, MAX_LNG = 0.206;

const COLOURS = ["#bababa", "#006837", "#1a9850", "#66bd63", 
                 "#a6d96a", "#d9ef8b", "#fee08b", "#fdae61", 
                 "#f46d43", "#d73027", "#a50026"]; 

// test that we can access the GEOJSON object from the londonBoroughs.geojson file
// GEOJSON["features"].forEach(function(d) {
//     console.log(d["properties"]["name"]);    
// })


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
    return { max: 10, data: newData };
}

function getEmissionsInfo(emissionsType){
    for(let i = 0; i < EMISSION_INFO.length; i++){
        if(EMISSION_INFO[i]['name'] === emissionsType){
            return EMISSION_INFO[i];
        }
    }
    return null;
}

function changeEmissionsInfoElements(emissionInfo){
    document.getElementById('title-emissions').innerHTML = emissionInfo['name'];
    document.getElementById('description-emissions').innerHTML = emissionInfo['description'];
    document.getElementById('health-effect-emissions').innerHTML = emissionInfo['health_effect'];
    document.getElementById('link-emissions').innerHTML = emissionInfo['link'];
}

function changeLocalAuthorityInfoElements(localAuthName, siteInfo){    
    const description = "There are " + siteInfo.length + " sites in the local authority. These are:"
    // debugger;
    const sitesList = siteInfo.map(function(d) { return d["name"]; });
    document.getElementById('title-local-authority').innerHTML = localAuthName;
    document.getElementById('description-local-authority').innerHTML = description;
    document.getElementById('list-sites').innerHTML = sitesList;
    // document.getElementById('link-emissions').innerHTML = emissionInfo['link'];
    
}

function getSitesInLocalAuthority(la_name){
    const la = LOCAL_AUTHORITIES.filter(function(d) { return d["name"] === la_name; });
    return SITES.filter(function(d) { return d["local_auth_id"] === la[0]["code"]; });
}

function getGeojsonForLocalAuthority(la_name){
    return GEOJSON['features'].filter(function(d){
        return d['properties']['name'] === la_name;
    });
}

function getMapLocalAuthBounds(coords){    
    const lats = [], lngs = [];    
    coords.forEach(function(d){
        if(isNaN(d[0])){ 
            console.log("Lng NaN: " + d[0]);
        } else {
            lngs.push(d[0]);
        }

        if(isNaN(d[1])){ 
            console.log("Lng NaN: " + d[1]);
        } else {
            lats.push(d[1]);
        }
    });
    return [[Math.min(...lats), Math.min(...lngs)], 
            [Math.max(...lats), Math.max(...lngs)]];
}

// ***************************************************************************************************
// Main 
// ***************************************************************************************************
function main(){
    // ----------------------------------------------------------------------------------------------
    // Get user location, adjust map to show either the user's location or all of London
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
	let baseLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
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
        "maxOpacity": 1.0,        // sets how opaque (i.e. non-transparent) the heatmap points are
        "scaleRadius": false,     // scales point radius based on map zoom         
        "useLocalExtrema": false, // use *global* heatmap values at all times (i.e. max *always* 1)       
        latField: 'lat',          // fieldname used for latitude
        lngField: 'lng',          // fieldname used for longitude
        valueField: 'value'       // fieldname used for heat value
    };
    // create the heatmap layer
    let heatmapLayer = new HeatmapOverlay(cfg);    

    // create the goejson polygon
    let geoJsonLayer = L.geoJSON();

    // create a circle for each marker
    // BETTER WAY: 
    // - add all the circles to a FeatureGroup
    // - can then bind the tooltip to every marker in the group
    // - can also control the z-order for the group, moving all circles to the front / back
    let siteList = [];
    let emissionList = [];
    for(let i = 0; i < SITES.length; i++){
        const mySite = EMISSION_LEVELS.find(function(elem) {
            return elem["Site name"] === SITES[i]["name"];
        });

        let siteEmission = 0;
        if(mySite !== undefined){            
            if(mySite[DEFAULT_EMISSIONS] !== null){
                siteEmission = mySite[DEFAULT_EMISSIONS];
            }
        }
        emissionList.push(siteEmission);

        let j = L.circleMarker([SITES[i]["latitude"], SITES[i]["longitude"]], {
            color: 'gray',
            fillColor: COLOURS[siteEmission],
            fillOpacity: 0.7,
            radius: 10        
        });     
        siteList.push(j);
    }
    const sitesLayer = L.featureGroup(siteList);
    // sitesLayer.bindTooltip(emissionList);
    // console.log(sitesLayer.getLayers());
    
    const emissionsLayers = {
        "Heatmap": heatmapLayer,
        "Site-points": sitesLayer
    };

    // create the map using the 'map' ID tag, and add the two layers
    let map = L.map("map", { 
        layers: [baseLayer, heatmapLayer, geoJsonLayer]//, sitesLayer]
    });

    // sitesLayer.bindTooltip("Y", {permanent: true,
    //                              direction: 'center', 
    //                              className: 'circle-text'
    //                             }).addTo(map);

    
    // SITES.forEach(function(d) {
    //     const mySite = EMISSION_LEVELS.find(function(elem) {
    //         return elem["Site name"] === d["name"];
    //     });
    //     let siteEmission = 0;
    //     if(mySite !== undefined){            
    //         if(mySite[DEFAULT_EMISSIONS] !== null){
    //             siteEmission = mySite[DEFAULT_EMISSIONS];
    //         }
    //     }

    //     const circle = L.circleMarker([d["latitude"], d["longitude"]], {
    //         color: 'gray',
    //         fillColor: COLOURS[siteEmission],
    //         fillOpacity: 0.7,
    //         radius: 10
    //     }).addTo(map);
        
    //     let tooltip = L.tooltip({
    //         permanent: true,
    //         direction: 'center',
    //         className: 'circle-text'
    //     }).setLatLng([d["latitude"], d["longitude"]])
    //       .setContent(siteEmission.toString())
    //       .addTo(map);

        // circle.bindTooltip(siteEmission.toString()).openTooltip();
    // });

    // ----------------------------------------------------------------------------------------------
    // Add some user controls
    // ----------------------------------------------------------------------------------------------
    L.control.scale().addTo(map);                   // scale in bottom-left corner
    L.control.layers(emissionsLayers).addTo(map);   // layer selector

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
    // Add an event listener, to update elements when the list-emissions drop-down changes
    // ----------------------------------------------------------------------------------------------
    const emissionsList = document.getElementById('list-emissions');
    // listen for a change in the emissions drop-down
    emissionsList.addEventListener("change", function(){
        // get the newly-selected element
        const newEmissionsType = document.getElementById('list-emissions').selectedOptions[0].text;
        
        // get the new emissions intensities
        heatmapLayer.setData(getEmissionsValues(newEmissionsType));
        console.log("map updated - change to " + newEmissionsType);

        // update the text of the emissions elements 
        changeEmissionsInfoElements(getEmissionsInfo(newEmissionsType));
    });

    // ----------------------------------------------------------------------------------------------
    // Add an event listener, to update elements when the list-london-areas drop-down changes
    // ----------------------------------------------------------------------------------------------
    const localAuthsList = document.getElementById('list-london-areas');
    // listen for a change in the local authorities drop-down
    localAuthsList.addEventListener("change", function(){
        // get the newly-selected element
        const newLocalAuth = document.getElementById('list-london-areas').selectedOptions[0].text;

        // get the boundary coords of the local authority and move the map to centre on it
        const newGeoJson = getGeojsonForLocalAuthority(newLocalAuth);
        map.fitBounds(getMapLocalAuthBounds(newGeoJson[0]["geometry"]["coordinates"][0][0]));
        
        // get rid of the existing local authority polygon layer, and draw a new LA polygon
        map.removeLayer(geoJsonLayer);
        geoJsonLayer = L.geoJSON(newGeoJson).addTo(map);

        console.log("Sites:");
        console.log(getSitesInLocalAuthority(newLocalAuth));
        // TODO: use the above to get the emissions collection sites in the local auth
        const sites = getSitesInLocalAuthority(newLocalAuth);
        // sites.forEach(function(d) {
        //     L.circle([d["latitude"], d["longitude"]], {
        //         color: 'red',
        //         fillColor: '#f03',
        //         fillOpacity: 0.5,
        //         alt: d["name"],
        //         radius: 300
        //     }).addTo(map);
        // });

        changeLocalAuthorityInfoElements(newLocalAuth, sites);
    });

    // map.on('zoomend', function() {
    //     var currentZoom = map.getZoom();
    //     var myRadius = currentZoom*(1/2); //or whatever ratio you prefer
    //     var myWeight = currentZoom*(1/5); //or whatever ratio you prefer
    //         layername.setStyle({radius: myRadius, weight: myWeight});
    // });

    // ----------------------------------------------------------------------------------------------
    // Add an event listener for the zoom-in button, to log current zoom level
    // ----------------------------------------------------------------------------------------------
    const zoomIn = document.getElementsByClassName("leaflet-control-zoom-in")[0];
    zoomIn.addEventListener("click", function(){
        console.log("Current zoom: " + map.getZoom());
    });

    // ----------------------------------------------------------------------------------------------
    // Generate emissions history graph
    // ----------------------------------------------------------------------------------------------
    function getDates(numDays) {
        let dates = [];
        const today = new Date();        
        dates.push(today.toLocaleDateString('en-GB'));
        for(let i = 1; i < numDays; i++){
            const newDate = new Date(today.getFullYear(), 
                                     today.getMonth(), 
                                     today.getDate() - i);
            dates.push(newDate.toLocaleDateString('en-GB'));
        }
        return dates.reverse();
    };

	const horizontalBarChartData = {
        labels: getDates(7), //['January', 'February', 'March', 'April', 'May', 'June', 'July'],
        datasets: [{
            label: 'Nitrogen Dioxide',
            backgroundColor: 'rgba(255, 0, 0, 0.3)',
            borderColor: 'rgba(255, 0, 0, 0.6)',
            borderWidth: 1,
            data: [7, 7, 8, 7, 8, 9, 10]
		}, {
            label: 'Sulphur Dioxide',
            backgroundColor: 'rgba(0, 0, 255, 0.3)',
            borderColor: 'rgba(0, 0, 255, 0.6)',
            data: [1, 3, 3, 2, 4, 5, 4]
        }, {
            label: 'Ozone',
            backgroundColor: 'rgba(0, 255, 0, 0.3)',
            borderColor: 'rgba(0, 255, 0, 0.6)',
            data: [2, 2, 3, 3, 2, 2, 3]
        }, {
            label: 'Carbon Monoxide',
            backgroundColor: 'rgba(33, 120, 120, 0.3)',
            borderColor: 'rgba(33, 120, 120, 0.6)',
            data: [3, 4, 3, 2, 3, 4, 5]
        }]

    };

    window.onload = function() {
        const ctx = document.getElementById('canvas-emission-history-graph').getContext('2d');
        window.myHorizontalBar = new Chart(ctx, {
            type: 'bar',
            data: horizontalBarChartData,
            options: {
                // Elements options apply to all of the options unless overridden in a dataset
                // In this case, we are setting the border of each horizontal bar to be 2px wide
                elements: {
                    rectangle: {
                        borderWidth: 2,
                    }
                },
                responsive: true,
                maintainAspectRatio: false, 
                legend: {
                    position: 'top',
                },            
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true, 
                        }
                    }]
                }
            }
        });

    };
}

// run the script
main();
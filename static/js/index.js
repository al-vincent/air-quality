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
 * */ 

"use strict";

// NOTE: wrt the consts below - should these be in main()?  E.g. am I adding to the global
// namespace by putting them here?
const CONFIG = JSON.parse(document.getElementById("config-id").textContent);
const EMISSION_LEVELS = JSON.parse(document.getElementById(CONFIG.CONSTANTS.JSON_SCRIPT.EMISSIONS_DATA_ID).textContent);
console.log("EMISSION_LEVELS:");
console.log(EMISSION_LEVELS);
const EMISSION_INFO = JSON.parse(document.getElementById(CONFIG.CONSTANTS.JSON_SCRIPT.EMISSIONS_INFO_ID).textContent);
const LOCAL_AUTHORITIES = JSON.parse(document.getElementById(CONFIG.CONSTANTS.JSON_SCRIPT.LOCAL_AUTHS_ID).textContent);
const SITES = JSON.parse(document.getElementById(CONFIG.CONSTANTS.JSON_SCRIPT.SITES_ID).textContent);

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

const TIMES = ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", 
               "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", 
               "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"];

// TODO: is there any point to these classes??           
const ACTIVE_TABLE_HEADERS = [{"text": "Sites", "class": "col-sites"}, 
                              {"text": "CO", "class": "col-co"}, 
                              {"text": "NO<sub>2</sub>", "class": "col-no2"},
                              {"text": "O<sub>3</sub>", "class": "col-o3"},
                              {"text": "PM10", "class": "col-pm10"},
                              {"text": "PM2.5", "class": "col-pm25"},
                              {"text": "SO<sub>2</sub>", "class": "col-so2"}];

// There *IS* a point to these classes, as the text is purposefully greyed
const INACTIVE_TABLE_HEADERS = [{"text": "Sites", "class": "inactive"},
                                {"text": "Opened", "class": "inactive"},
                                {"text": "Closed", "class": "inactive"},
                                {"text": "Type", "class": "inactive"}];

// Refs to each of the emissions graphs that can be drawn for a site (declaring them
// globally allows the graphs to be easily destroyed)                                
const CO_GRAPH = null, NO2_GRAPH = null, O3_GRAPH = null, 
      PM10_GRAPH = null, PM25_GRAPH = null, SO2_GRAPH = null;

// an emissions lookup object, containing useful info about each of the emissions types.
// rgba vals are used in the emissions graphs
const EMISSION_LOOKUP = {"CO": {"name": "Carbon Monoxide",
                                // "elementID": CONFIG.HTML.SITES.CO.CHART.ID,
                                "backgroundColor": "rgba(255, 0, 0, 0.3)",
                                "borderColor": "rgba(255, 0, 0, 0.6)",
                                "chartObject": CO_GRAPH},
                        "NO2": {"name": "Nitrogen Dioxide",
                                // "elementID": CONFIG.HTML.SITES.NO2.CHART.ID,
                                "backgroundColor": "rgba(0, 255, 0, 0.3)",
                                "borderColor": "rgba(0, 255, 0, 0.6)",
                                "chartObject": NO2_GRAPH},
                        "O3": {"name": "Ozone",
                            //    "elementID": CONFIG.HTML.SITES.O3.CHART.ID,
                               "backgroundColor": "rgba(0, 0, 255, 0.3)",
                               "borderColor": "rgba(0, 0, 255, 0.6)",
                               "chartObject": O3_GRAPH},
                        "PM10": {"name": "PM10 Particulate",
                                //  "elementID": CONFIG.HTML.SITES.PM10.CHART.ID,
                                 "backgroundColor": "rgba(33, 120, 120, 0.3)",
                                 "borderColor": "rgba(33, 120, 120, 0.6)",
                                 "chartObject": PM10_GRAPH},
                        "PM25": {"name": "PM2.5 Particulate",
                                //  "elementID": CONFIG.HTML.SITES.PM10.CHART.ID,
                                 "backgroundColor": "rgba(120, 33, 120, 0.3)",
                                 "borderColor": "rgba(120, 33, 120, 0.6)",
                                 "chartObject": PM25_GRAPH},
                        "SO2": {"name": "Sulphur Dioxide",
                                // "elementID": CONFIG.HTML.SITES.SO2.CHART.ID,
                                "backgroundColor": "rgba(120, 120, 33, 0.3)",
                                "borderColor": "rgba(120, 120, 33, 0.6)",
                                "chartObject": SO2_GRAPH}
                        };

// Root of the LondonAir API
const API_ROOT = "https://api.erg.kcl.ac.uk/AirQuality/";

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

/** 
 * @summary Get simple summary information for the emissions type, specifically:
 * - a description of the emission;
 * - its effects on people's health;
 * - a URL for more information on the emission.
 * @param emissionsType (str), the name of the emission (e.g. "Nitrogen Dioxide")
 * @returns an object with each of the 
 * ^^ *** CHECK, FINISH THE ABOVE!! ***
*/
function getEmissionsInfo(emissionsType){
    for(let i = 0; i < EMISSION_INFO.length; i++){
        if(EMISSION_INFO[i]['name'] === emissionsType){
            return EMISSION_INFO[i];
        }
    }
    return null;
}

function changeEmissionsInfoElements(emissionInfo){    
    document.getElementById(CONFIG.HTML.EMISSIONS.TITLE.ID).innerHTML = emissionInfo['name'];
    document.getElementById(CONFIG.HTML.EMISSIONS.DESCRIPTION.BODY.ID).innerHTML = emissionInfo['description'];    
    document.getElementById(CONFIG.HTML.EMISSIONS.HEALTH_EFFECTS.BODY.ID).innerHTML = emissionInfo['health_effect'];
    // document.getElementById('link-emissions').innerHTML = emissionInfo['link'];
}

function createTableHead(tableId, headers){
    const table = document.getElementById(tableId);
    const headerRow = table.createTHead().insertRow(0);
    for(let i = 0; i < headers.length; i++){
        const cellStr = '<th class="' + headers[i]["class"] + '">' + headers[i]["text"] + '</th>';
        headerRow.insertCell(i).outerHTML = cellStr;        
    }        
}

function addTableRow(tableId, position, info){
    const table = document.getElementById(tableId);
    const row = table.insertRow(position);
    row.setAttribute('data-site', info[0]["value"]);
    for(let i = 0; i < info.length; i++){
        const cell = row.insertCell(i);
        const text = i === 0 ? shortSiteName(info[i]["value"]) : info[i]["value"];
        cell.innerHTML = text;
        cell.setAttribute("class", info[i]["class"]);
    }
    row.addEventListener("click", function(){
        // console.log(this.getAttribute("data-site"));
        showSiteEmissions(this.getAttribute("data-site"));
    });  
}

function parseResponse(jsonResponse){
    let data = {"CO": [], "NO2": [], "O3": [], "PM10": [], "PM25": [], "SO2": []};
    // get today's air quality data
    jsonResponse["AirQualityData"]["Data"].forEach(function(d){
        if(d["@SpeciesCode"] in data){
            const value = d["@Value"] !== "" ? parseFloat(d["@Value"]) : 0;
            data[d["@SpeciesCode"]].push(value);
        }
    });
    // each array should have a value for the times 00:00 -> 23:00, so add trailing
    // zeros for any timestamp where there isn't data yet.
    const keys = Object.keys(data);
    keys.forEach(function(d){
        const numZeros = TIMES.length - data[d].length;
        data[d].concat(Array(numZeros).fill(0));
    })
    return data;
}

function clearGraphs(){
    // clear all charts, i.e. DOM elements with class 'chart'
    const keys = Object.keys(EMISSION_LOOKUP);
    keys.forEach(function(d){
        if(EMISSION_LOOKUP[d]["chartObject"] !== null){
            EMISSION_LOOKUP[d]["chartObject"].destroy();
        }
    })

    // remove all chart-container classes
    const chartRows = document.getElementsByClassName("row-chart");
    for(let i = 0; i < chartRows.length; i++){
        chartRows[i].classList.add("row-hidden");
    }
}

function plotDaysEmissionsGraph(emissionCode, graphData){
    const barChartData = {        
        labels: TIMES, 
        datasets: [{
            backgroundColor: EMISSION_LOOKUP[emissionCode]["backgroundColor"],
            borderColor: EMISSION_LOOKUP[emissionCode]["borderColor"],
            borderWidth: 1,
            data: graphData 
		}]
    };

    const element = document.getElementById(CONFIG.HTML.SITES[emissionCode].CHART.ID);
    element.parentElement.parentElement.classList.remove("row-hidden");
    const ctx = element.getContext('2d');
    EMISSION_LOOKUP[emissionCode]["chartObject"] = new Chart(ctx, {
        type: 'bar',
        data: barChartData,
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
                display: false,
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
}

function makeRequest(URL) {
    const httpRequest = new XMLHttpRequest();

    if (!httpRequest) {
      console.log('Giving up :( Cannot create an XMLHTTP instance');
      return false;
    }

    httpRequest.open('GET', URL, true);
    httpRequest.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            console.log("Success! JSON response:")
            const response = JSON.parse(this.responseText);
            const emissionsData = parseResponse(response);
            console.log(emissionsData);
            const keys = Object.keys(emissionsData);
            keys.forEach(function(d){
                // if the graph data is all zeros, we don't want to plot it
                const allZero = emissionsData[d].every(function(e){ 
                    return e === 0;
                });
                if(emissionsData[d].length > 0 && !allZero){
                    plotDaysEmissionsGraph(d, emissionsData[d]);
                }
            });
        }
    };
    httpRequest.send();
}

function formatDate(date){
    const dateArray = date.toDateString().split(" ");
    return dateArray[2] + dateArray[1] + dateArray[3];
}

function showSiteEmissions(siteName){
    clearGraphs();
    const siteCode = SITES.find(function(d) { return d["name"] === siteName })["code"];
    document.getElementById(CONFIG.HTML.SITES.TITLE.ID).innerHTML = siteName;
    const today = new Date();
    const tomorrow = new Date(today.getFullYear(), today.getMonth(), today.getDate() + 1);
    const startDate = formatDate(today);
    const endDate = formatDate(tomorrow);
    const url = API_ROOT.concat("Data/Site/SiteCode=", siteCode, "/StartDate=", startDate, "/EndDate=", endDate, "/Json");
    makeRequest(url);
}

function shortSiteName(fullSiteName){
    return fullSiteName.includes("- ") ? fullSiteName.substr(fullSiteName.indexOf("- ") + 2,) : fullSiteName;
}

function changeLocalAuthorityInfoElements(localAuthName, siteInfo){
    // unhide the local-authority jumbotron
    document.getElementById(CONFIG.HTML.LOCAL_AUTHS.CONTAINER_ID).classList.remove("row-hidden");

    // set the title to be the local auth selected
    document.getElementById(CONFIG.HTML.LOCAL_AUTHS.TITLE.ID).innerHTML = localAuthName;
    
    // filter EMISSION_LEVELS data to get current emissions for active sites in this LA
    // NOTE: this is necessary, because EMISSION_LEVELS contains the current emissions for 
    // each site, and siteInfo doesn't. 
    const activeSiteInfo = EMISSION_LEVELS.filter(function(d){ 
        return d["Local Authority name"] === localAuthName; 
    });
    console.log("activeSiteInfo:");
    console.log(activeSiteInfo);

    // setup active site info
    let description = "There are " + activeSiteInfo.length + " active sites in the local authority:"
    document.getElementById(CONFIG.HTML.LOCAL_AUTHS.ACTIVE_SITES.DESCRIPTION_ID).innerHTML = description;
    document.getElementById(CONFIG.HTML.LOCAL_AUTHS.ACTIVE_SITES.TABLE_ID).innerHTML = "";
    if(activeSiteInfo.length > 0) { 
        createTableHead(CONFIG.HTML.LOCAL_AUTHS.ACTIVE_SITES.TABLE_ID, ACTIVE_TABLE_HEADERS); 
    }
    
    // setup inactive site info
    description = "There are " + (siteInfo.length - activeSiteInfo.length) + " inactive sites in the local authority:"
    document.getElementById(CONFIG.HTML.LOCAL_AUTHS.INACTIVE_SITES.DESCRIPTION_ID).innerHTML = description;
    document.getElementById(CONFIG.HTML.LOCAL_AUTHS.INACTIVE_SITES.TABLE_ID).innerHTML = "";
    if(activeSiteInfo.length < siteInfo.length ){
        createTableHead(CONFIG.HTML.LOCAL_AUTHS.INACTIVE_SITES.TABLE_ID, INACTIVE_TABLE_HEADERS); 
    }

    // add info for each site
    let i = 1, j = 1;
    let inactiveSiteInfo = [];
    let firstSite = null;
    siteInfo.forEach( function(d){
        if(i === 1){ firstSite = d["name"]; }
        // strip any unwanted text from the site-name
        //const siteName = d["name"].includes("- ") ? d["name"].substr(d["name"].indexOf("- ") + 2,) : d["name"];
        // set emissions levels for active sites
        if(d["site_still_active"]){
            const keys = Object.keys(EMISSION_LOOKUP);
            // although the *site* is active, it probably won't collect all emissions; default is "doesn't collect"
            const emissions = Array(keys.length).fill({"value": "-", "class": "cell inactive"})
            emissions.splice(0,0,{"value": d["name"], "class": i});

            const mySite = activeSiteInfo.find(function(e) { return e["Site name"] === d["name"]; });
            let k = 1;
            keys.forEach(function(elem){
                if(mySite[EMISSION_LOOKUP[elem]["name"]] !== null && mySite[EMISSION_LOOKUP[elem]["name"]] !== 0){
                    const val = {"value": mySite[EMISSION_LOOKUP[elem]["name"]],
                                 "class": "active-table cell cell-level-"+String(mySite[EMISSION_LOOKUP[elem]["name"]])};
                    emissions[k] = val;
                }
                k++;
            });

            addTableRow("table-active-sites", i, emissions);
            i++;
        } else {
            inactiveSiteInfo.push(d);
            const data = [{"value": shortSiteName(d["name"]), "class": "inactive"},
                        {"value": new Date(d["site_date_open"]).toDateString().slice(4,), "class": "inactive"},
                        {"value": new Date(d["site_date_closed"]).toDateString().slice(4,), "class": "inactive"},
                        {"value": d["site_type"], "class": "inactive"}];
            addTableRow("table-inactive-sites", j, data);
            j++;
        }        
    });
    console.log("inactiveSiteInfo:");
    console.log(inactiveSiteInfo); 
    
    // document.getElementById('link-emissions').innerHTML = emissionInfo['link'];
    showSiteEmissions(firstSite);
}

function getSitesInLocalAuthority(la_name){
    const la = LOCAL_AUTHORITIES.find(function(d) { return d["name"] === la_name; });
    return SITES.filter(function(d) { return d["local_auth_id"] === la["code"]; });
}

function getGeojsonForLocalAuthority(la_name){
    return GEOJSON['features'].find(function(d){
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
    let map = L.map(CONFIG.HTML.MAP.ID, { 
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
    document.getElementById(CONFIG.HTML.LISTS.EMISSION_LIST_ID).value = DEFAULT_CODE;    
    heatmapLayer.setData(getEmissionsValues(DEFAULT_EMISSIONS));

    // change the text of the emissions elements to be about emission we're looking at
    changeEmissionsInfoElements(getEmissionsInfo(DEFAULT_EMISSIONS));

    // ----------------------------------------------------------------------------------------------
    // Add an event listener, to update elements when the list-emissions drop-down changes
    // ----------------------------------------------------------------------------------------------
    const emissionsList = document.getElementById(CONFIG.HTML.LISTS.EMISSION_LIST_ID);
    // listen for a change in the emissions drop-down
    emissionsList.addEventListener("change", function(){
        // get the newly-selected element
        const newEmissionsType = emissionsList.selectedOptions[0].text;
        
        // get the new emissions intensities
        heatmapLayer.setData(getEmissionsValues(newEmissionsType));
        console.log("map updated - change to " + newEmissionsType);

        // update the text of the emissions elements 
        changeEmissionsInfoElements(getEmissionsInfo(newEmissionsType));
    });

    // ----------------------------------------------------------------------------------------------
    // Add an event listener, to update elements when the list-london-areas drop-down changes
    // ----------------------------------------------------------------------------------------------
    const localAuthsList = document.getElementById(CONFIG.HTML.LISTS.LOCAL_AUTHS_LIST_ID);
    // listen for a change in the local authorities drop-down
    localAuthsList.addEventListener("change", function(){
        // get the newly-selected element
        const newLocalAuth = localAuthsList.selectedOptions[0].text;
        if(newLocalAuth !== "All Local Authorities") {
            // get the boundary coords of the local authority and move the map to centre on it
            const newGeoJson = getGeojsonForLocalAuthority(newLocalAuth);
            map.fitBounds(getMapLocalAuthBounds(newGeoJson["geometry"]["coordinates"][0][0]));
            
            // get rid of the existing local authority polygon layer, and draw a new LA polygon
            map.removeLayer(geoJsonLayer);
            geoJsonLayer = L.geoJSON(newGeoJson).addTo(map);

            console.log("Sites:");
            console.log(getSitesInLocalAuthority(newLocalAuth));
            
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
        } else {
            // TODO: reset the map view, either to the user location or to the London map
            const element = document.getElementById(CONFIG.HTML.LOCAL_AUTHS.CONTAINER_ID);
            if(!element.classList.contains("row-hidden")) {
                element.classList.add("row-hidden");
            }
        }
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
}

// run the script
main();
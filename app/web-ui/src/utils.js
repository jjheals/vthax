export function toTitleCase(str) {
    return str
        .toLowerCase() // Convert the string to lowercase
        .split(' ') // Split the string into words
        .map(word => word.charAt(0).toUpperCase() + word.slice(1)) // Capitalize the first letter of each word
        .join(' '); // Join the words back into a single string
}


/**
 * @deprecated
 * @param { Object } pathRanks 
 * @returns 
 */
export function rankPaths(pathRanks) { 
    const totalCosts = Object.keys(pathRanks).map(path => {
        const costs = Object.values(pathRanks[pathRanks]);
        const totalCost = costs.reduce((sum, cost) => sum + cost, 0);
        return { path, totalCost };
    });
      
    // Step 2: Sort paths by total cost
    totalCosts.sort((a, b) => a.totalCost - b.totalCost);
    
    // Return
    return totalCosts
}



/**
 * @function getInputParamsData retrieves the data from the API on init of the page.
 * @returns { null }
 */
export async function getInputParamsData(apiBaseUrl, options) { 
    // Get the data from the API 
    const response = await fetch(`${apiBaseUrl}/get-input-params`, options);
    const responseJson = await response.json();
    return responseJson;
}

export function findLeastLatitude(paths) {
    let leastLatitudes = {};
    let globalLeastLatitude = Infinity;
    for (const pathName in paths) {
        if (paths.hasOwnProperty(pathName)) {
            const pathLatitudes = paths[pathName].path.map(([lat, lon]) => lat);
            const leastLatitude = Math.min(...pathLatitudes);
            leastLatitudes[pathName] = leastLatitude;

            if (leastLatitude < globalLeastLatitude) {
                globalLeastLatitude = leastLatitude;
            }
        }
    }
    return globalLeastLatitude;
}

export function findAverageLongitude(paths) {
    const { totalSum, count } = Object.values(paths).reduce((acc, { path }) => {
        const longitudes = path.map(([lat, lon]) => lon);
        const sum = longitudes.reduce((sum, lon) => sum + lon, 0);
        acc.totalSum += sum;
        acc.count += longitudes.length;
        return acc;
    }, { totalSum: 0, count: 0 });

    return totalSum / count;
}

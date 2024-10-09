#include <iostream>  // cout
#include <stdlib.h>  // rand
#include <math.h>    // sqrt, pow
#include <omp.h>     // OpenMP
#include <string.h>  // memset
#include <algorithm>
#include "Timer.h"
#include "Trip.h"

#define CHROMOSOMES    50000 // 50000 different trips
#define CITIES         36    // 36 cities = ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789
#define TOP_X          25000 // top optimal 25%
#define MUTATE_RATE    45    // optimal 50%

using namespace std;

/*
 * Evaluates each trip (or chromosome) and sort them out
 */

int partition(Trip trips[], int low, int high) {
    Trip pivot = trips[low];
    while (low< high)
    {
        while (low< high && trips[high].fitness >= pivot.fitness)
            high--;
        trips[low] = trips[high];
        while (low < high && trips[low].fitness <= pivot.fitness)
            low++;
        trips[high] = trips[low]; 
    }
    trips[low] = pivot;
    return low;  
}

void quicSort(Trip trips[], int low, int high) {
    if (low < high) {
        int pos = partition(trips, low, high);
        quicSort(trips, low, pos-1);
        quicSort(trips, pos+1, high);
    }
}

bool tripCompare(Trip A, Trip B) {
    return A.fitness < B.fitness;
}

void evaluate( Trip trip[CHROMOSOMES], int coordinates[CITIES][2] ) {
    // calculating the distance of each trip
    int i, lastCityXCord, lastCityYCord;
    float totalDistance;
#pragma omp parallel for private(i, totalDistance, lastCityXCord, lastCityYCord)
    for (int i=0; i < CHROMOSOMES; i ++) {
        float totalDistance = 0;
        int lastCityXCord = 0;
        int lastCityYCord = 0;
        for (int city=0; city < CITIES; city++) {
            int cityIndex = ( trip[i].itinerary[city] >= 'A' ) ? trip[i].itinerary[city] - 'A' : trip[i].itinerary[city] - '0' + 26;
            totalDistance += sqrt(pow(coordinates[cityIndex][0] - lastCityXCord, 2) + pow(coordinates[cityIndex][1] - lastCityYCord, 2));
            lastCityXCord = coordinates[cityIndex][0];
            lastCityYCord = coordinates[cityIndex][1];
        }
        // assign fitness
        trip[i].fitness = totalDistance;
    }
    // sorting
    std::sort(trip, trip + CHROMOSOMES, tripCompare);
    // Debugging quick sort
    if ( DEBUG ) {
        for (int i=0; i < CHROMOSOMES; i++) {
            cout << trip[i].fitness << endl;
        }
    }
}

/*
 * Generates new TOP_X offsprings from TOP_X parents.
 * Noe that the i-th and (i+1)-th offsprings are created from the i-th and (i+1)-th parents
 */
void crossover( Trip parents[TOP_X], Trip offsprings[TOP_X], int coordinates[CITIES][2] ) {

    //calculating the distance map
    float distanceMap[CITIES][CITIES];
    for (int i=0; i<CITIES; i++) {
        distanceMap[i][i] = -1;
        for (int j=i+1; j<CITIES; j++) {
            float dist = sqrt(pow(coordinates[i][0] - coordinates[j][0], 2) + pow(coordinates[i][1] - coordinates[j][1], 2));
            distanceMap[i][j] = dist;
            distanceMap[j][i] = dist;
        }
    }
    // generating child[i] and child[i+1]
    for (int i=0; i<TOP_X-1; i+=2) {
        offsprings[i].itinerary[0] = parents[i].itinerary[0];
        // usage list indication cities traveled or not
        int travelHistory[CITIES] = {0};
        for (int j=1; j<CITIES; j++) {
            int previousCityIndex = ( offsprings[i].itinerary[j-1] >= 'A' ) ? offsprings[i].itinerary[j-1] - 'A' : offsprings[i].itinerary[j-1] - '0' + 26;
            travelHistory[previousCityIndex] = 1;
            float shortestDist = 999999;
            int nearestAvailableCityIndex = -1;
            // looking for the nearest city to j
            for (int k=0; k<CITIES;k++) {
                if (distanceMap[previousCityIndex][k] < shortestDist && travelHistory[k] == 0) {
                shortestDist = distanceMap[previousCityIndex][k];
                nearestAvailableCityIndex = k;
            }
            }
            offsprings[i].itinerary[j] = (nearestAvailableCityIndex < 26) ? 'A' + nearestAvailableCityIndex : nearestAvailableCityIndex - 26 + '0';
        }
        //generate child[i+1]
        for (int j=0; j<CITIES-1; j+=2) {
            offsprings[i+1].itinerary[j] = offsprings[i].itinerary[j+1];
            offsprings[i+1].itinerary[j+1] = offsprings[i].itinerary[j];
        }
    }
}

void crossoverB( Trip parents[TOP_X], Trip offsprings[TOP_X], int coordinates[CITIES][2] ) {
    float distanceMap[CITIES][CITIES];
    int i;
#pragma omp parallel for private(i) shared(distanceMap)
    for (int i=0; i<CITIES; i++) {
        distanceMap[i][i] = -1;
        for (int j=i+1; j<CITIES; j++) {
            float dist = sqrt(pow(coordinates[i][0] - coordinates[j][0], 2) + pow(coordinates[i][1] - coordinates[j][1], 2));
            distanceMap[i][j] = dist;
            distanceMap[j][i] = dist;
        }
    }
    // generating child[i] and child[i+1]
#pragma omp parallel for
    for (int i=0; i<TOP_X-1; i+=2) {
        offsprings[i].itinerary[0] = parents[i].itinerary[0];
        int travelHistory[CITIES] = {0};
        for (int j=1; j<CITIES; j++) {
            char previousCity = offsprings[i].itinerary[j-1];
            int previousCityIndex = ( offsprings[i].itinerary[j-1] >= 'A' ) ? offsprings[i].itinerary[j-1] - 'A' : offsprings[i].itinerary[j-1] - '0' + 26;
            travelHistory[previousCityIndex] = 1;
            char nextCityA, nextCityB;           
            // getiing the near city of the leaving city
            for(int k=0; k< CITIES-1; k++) {
                if (parents[i].itinerary[k] == previousCity) {
                    nextCityA = parents[i].itinerary[k+1];
                }
                if (parents[i+1].itinerary[k] == previousCity) {
                    nextCityB =parents[i+1].itinerary[k+1];
                }
            }
            // If the leaving city is the last one, choose the first city as the leaving city
            if (parents[i].itinerary[CITIES-1] == previousCity) {
                nextCityA = parents[i].itinerary[0];
            }
            if (parents[i+1].itinerary[CITIES-1] == previousCity) {
                nextCityB = parents[i+1].itinerary[0];
            }
            // comparing distance and usage map to decide next city
            int cityAIdx = (nextCityA >= 'A') ? nextCityA - 'A' : nextCityA - '0' +26;
            int cityBIdx = (nextCityB >= 'A') ? nextCityB - 'A' : nextCityB - '0' +26;
            bool isAReachable = !travelHistory[cityAIdx];
            bool isBReachable = !travelHistory[cityBIdx];
            char nextCity;
            if (isAReachable && isBReachable) {
                if (distanceMap[previousCityIndex][cityAIdx] <= distanceMap[previousCityIndex][cityBIdx]) {
                    nextCity = nextCityA;
                } else {
                    nextCity = nextCityB;
                }
            } else if (isAReachable || isBReachable) {
                if (isAReachable) {
                    nextCity = nextCityA;
                } else {
                    nextCity = nextCityB;
                }
            } else if (!isAReachable && !isBReachable) {
                for(int k=0; k< CITIES; k++) {
                    if (travelHistory[k] == 0) {
                        nextCity = (k < 26) ? 'A' + k : k - 26 + '0';
                        break;
                    }
                }
            }
            offsprings[i].itinerary[j] = nextCity;
        }
        //generate child[i+1]
        for (int j=0; j<CITIES-1; j+=2) {
            offsprings[i+1].itinerary[j] = offsprings[i].itinerary[j+1];
            offsprings[i+1].itinerary[j+1] = offsprings[i].itinerary[j];
        }
    }
}

void crossoverC( Trip parents[TOP_X], Trip offsprings[TOP_X], int coordinates[CITIES][2] ) {
    //generating child[i] and child[i+1]
    for (int i=0; i<TOP_X-1; i+=2) {
        // generating cross over slice of genes' startIndex and endIndex
        int idxStart = rand()%(CITIES-1); //[0,34]
        int idxEnd = idxStart + 1 + rand()%(CITIES - 1 - idxStart); //[idxStart+1,35]
        strncpy(offsprings[i].itinerary, parents[i].itinerary, CITIES+1);
        strncpy(offsprings[i+1].itinerary, parents[i+1].itinerary, CITIES+1);
        // using index map to swap
        int idxMapOne[CITIES], idxMapTwo[CITIES];
        for (int j=0; j<CITIES; j++) {
            idxMapOne[( parents[i].itinerary[j] >= 'A' ) ? parents[i].itinerary[j] - 'A' : parents[i].itinerary[j] - '0' + 26] = j;
            idxMapTwo[( parents[i+1].itinerary[j] >= 'A') ? parents[i+1].itinerary[j] - 'A' : parents[i+1].itinerary[j] - '0' + 26] = j;
        } 
        for(int idx=idxStart; idx<= idxEnd; idx++) {
            // generating child[i].itinerary
            char tmp = offsprings[i].itinerary[idx];
            int idxC1 = idxMapOne[(offsprings[i+1].itinerary[idx] >= 'A') ? offsprings[i+1].itinerary[idx] - 'A' : offsprings[i+1].itinerary[idx] - '0' + 26];
            offsprings[i].itinerary[idx] = offsprings[i].itinerary[idxC1];
            offsprings[i].itinerary[idxC1] = tmp;
            // generating child[i+1].itinerary
            tmp = offsprings[i+1].itinerary[idx];
            int idxC2 = idxMapTwo[(offsprings[i].itinerary[idx] >= 'A') ? offsprings[i].itinerary[idx] - 'A' : offsprings[i].itinerary[idx] - '0' + 26];
            offsprings[i+1].itinerary[idx] = offsprings[i+1].itinerary[idxC2];
            offsprings[i+1].itinerary[idxC2] = tmp;
        }
    }
}


/*
 * Mutate a pair of genes in each offspring.
 */
void mutateSwap( Trip offsprings[TOP_X] ) {
    int swapPosition[2] = {rand()%CITIES, rand()%CITIES};
    for (int i=0; i<TOP_X; i++) {
        if (rand()% 100 < MUTATE_RATE) {
            char tmp = offsprings[i].itinerary[swapPosition[0]];
            offsprings[i].itinerary[swapPosition[0]] = offsprings[i].itinerary[swapPosition[1]];
            offsprings[i].itinerary[swapPosition[1]] = tmp;
        }
    }
}

void mutate( Trip offsprings[TOP_X] ) {
    int rateList[TOP_X], idxStartList[TOP_X], idxEndList[TOP_X];
    for (int i=0; i<TOP_X;i++) {
        rateList[i] = rand() % 100;
        idxStartList[i] = rand()%(CITIES-1); //[0,34]
        idxEndList[i] = idxStartList[i] + 1 + rand()%(CITIES -1 - idxStartList[i]); //[idxStart+1,35]
    }
    int i, idxStart, idxEnd;
#pragma omp parallel for private(i, idxStart, idxEnd) shared(rateList, idxStartList, idxEndList, offsprings)
    for (int i=0; i<TOP_X; i++) {
        if (rateList[i] < MUTATE_RATE) {
            idxStart = idxStartList[i];
            idxEnd = idxEndList[i];
            while (idxStart < idxEnd)
            {
                char tmp = offsprings[i].itinerary[idxStart];
                offsprings[i].itinerary[idxStart] = offsprings[i].itinerary[idxEnd];
                offsprings[i].itinerary[idxEnd] = tmp;
                idxStart++;
                idxEnd--;
            }
        }

    }
}

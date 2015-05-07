'use strict';

var libraryUtilApp = angular.module('libraryUtilApp', []);

libraryUtilApp.filter('reservationStatus', function () {
    return function(isReserved) {
        return isReserved ? '\u2713 Reserved' : '\u2718 Canceled';
    }
}).filter('copyStatus', function () {
    return function(isAvailable) {
        return isAvailable ? '\u2713 Available' : '\u2718 Unavailable';
    }
}).filter('returnDatetime', function() {
    return function(bDatetime) {
        var max_borrow_days = 20;
        return moment(bDatetime).add(max_borrow_days, 'days')
    }
});
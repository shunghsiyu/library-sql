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
}).filter('adminCopyAvailable', function () {
    return function(copy) {
        if(copy.borrower) {
            return false;
        }
        return copy.reserver === null;
    }
}).filter('adminCopyStatus', function () {
    return function(copy) {
        if(copy.borrower) {
            return '\u2718 Borrowed by ' + copy.borrower.name + ' (id: ' + copy.borrower.reader_id + ')';
        }
        else if(copy.reserver) {
            return '\u2718 Reserved by ' + copy.reserver.name + ' (id: ' + copy.reserver.reader_id + ')';
        } else {
            return '\u2713 Available'
        }
    }
});
'use strict';

var libraryReaderApp = angular.module('libraryReaderApp', ['angularMoment', 'ui.router', 'ui.bootstrap', 'ui.select']);

libraryReaderApp.factory('readerIdService', function($http, $q) {
    var deferred = $q.defer();
    $http.get('/api/info').success(function(data) {
        deferred.resolve(data.reader_id)
    }).error(function(status) {
        deferred.reject(status)
    });
    return function() {
        return deferred.promise;
    }
}).factory('readerInfoService', function($http, $q, readerIdService) {
    var promise = readerIdService().then(function(reader_id) {
        return $http.get('/api/readers/'+reader_id)
    }).then(function(response) {
        return response.data
    });
    return function() {
        return promise;
    }
});

libraryReaderApp.controller('ReaderCtrl', function($scope, readerInfoService) {
    // None
}).controller('ReserveCtrl', function($scope, reader) {
    console.log(reader)
});

libraryReaderApp.config(function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/home');

    $stateProvider.state('home', {
        url: '/home',
        templateUrl: '/partial/home.html'
    }).state('search', {
        url: '/search',
        templateUrl: '/partial/search.html'
    }).state('reserves', {
        url: '/reserves',
        templateUrl: '/partial/reserves.html',
        controller: 'ReserveCtrl',
        resolve: {
            reader: function(readerInfoService) {
                return readerInfoService();
            }
        }
    }).state('borrows', {
        url: '/borrows',
        templateUrl: '/partial/borrows.html'
    });
});


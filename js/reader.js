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
    var deferred = $q.defer();
    readerIdService().then(function(reader_id) {
        $http.get('/api/readers/'+reader_id).success(function(data) {
            deferred.resolve(data)
        }).error(function(status) {
            deferred.reject(status)
        })
    });
    return function() {
        return deferred.promise;
    }
});

libraryReaderApp.controller('ReaderCtrl', function($scope, readerInfoService) {
    // None
}).controller('ReserveCtrl', function($scope, reader, reserveInfoService) {
    console.log(reserveInfoService())
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


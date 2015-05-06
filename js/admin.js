'use strict';

var libraryAdminApp = angular.module('libraryAdminApp', ['ngResource', 'angularMoment', 'ui.router', 'ui.bootstrap', 'ui.select']);

libraryAdminApp.factory('averageFineResource', function($resource) {
    return $resource('/api/readers/average_fine', {}, {
        'get': {method: 'GET'}
    });
}).factory('readerResource', function($resource) {
    return $resource('/api/readers/', {}, {
        'add': {method: 'POST'}
    });
});

libraryAdminApp.controller('libraryInfoCtrl', function($scope, averageFines) {
    $scope.averageFines = averageFines.results;
}).controller('addReaderCtrl', function($scope, readerResource) {
    $scope.add = function() {
        readerResource.add($scope.readerToAdd);
    }
});

libraryAdminApp.config(['$resourceProvider', function($resourceProvider) {
  // Don't strip trailing slashes from calculated URLs
  $resourceProvider.defaults.stripTrailingSlashes = false;
}]).config(function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/home');

    $stateProvider.state('home', {
        url: '/home',
        templateUrl: '/partial/library.html',
        controller: 'libraryInfoCtrl',
        resolve: {
            averageFines: function(averageFineResource) {
                return averageFineResource.get().$promise;
            }
        }
    }).state('branches', {
        url: '/branches',
        templateUrl: '/partial/branches.html'
    }).state('addReader', {
        url: '/addReader',
        templateUrl: '/partial/add_reader.html',
        controller: 'addReaderCtrl'
    }).state('addCopy', {
        url: '/addCopy',
        templateUrl: '/partial/add_copy.html'
    }).state('searchCopies', {
        url: '/searchCopies',
        templateUrl: '/partial/search_copies.html'
    });
});
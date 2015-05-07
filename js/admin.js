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
}).factory('branchesResource', function($resource) {
    return $resource('/api/branches/', {}, {
        'get': {method: 'GET'}
    });
}).factory('branchResource', function($resource) {
    return function(branchId) {
        return $resource('/api/branches/:branch_id',
            {branch_id: branchId}, {
                'get': {method: 'GET'}
            }, {stripTrailingSlashes: true});
    };
});

libraryAdminApp.controller('libraryInfoCtrl', function($scope, averageFines) {
    $scope.averageFines = averageFines.results;
}).controller('addReaderCtrl', function($scope, readerResource) {
    $scope.add = function() {
        if($scope.addReaderForm.$invalid) {
            return;
        }
        readerResource.add($scope.readerToAdd);
    }
}).controller('branchInfoCtrl', function($scope, branchesData, branchResource) {
    $scope.branches = branchesData.branches;
    $scope.load = function(branch) {
        $scope.branch = branchResource(branch.lib_id).get();
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
        templateUrl: '/partial/branches.html',
        controller: 'branchInfoCtrl',
        resolve: {
            branchesData: function(branchesResource) {
                return branchesResource.get().$promise;
            }
        }
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
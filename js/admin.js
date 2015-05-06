'use strict';

var libraryAdminApp = angular.module('libraryAdminApp', ['ngResource', 'angularMoment', 'ui.router', 'ui.bootstrap', 'ui.select']);

libraryAdminApp.config(function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/home');

    $stateProvider.state('home', {
        url: '/home',
        templateUrl: '/partial/library.html'
    }).state('branches', {
        url: '/branches',
        templateUrl: '/partial/branches.html'
    }).state('addReader', {
        url: '/addReader',
        templateUrl: '/partial/add_reader.html'
    }).state('addCopy', {
        url: '/addCopy',
        templateUrl: '/partial/add_copy.html'
    }).state('searchCopies', {
        url: '/searchCopies',
        templateUrl: '/partial/search_copies.html'
    });
});
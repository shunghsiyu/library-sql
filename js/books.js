'use strict';

var libraryApp = angular.module('libraryApp', ['angularMoment']);

libraryApp.controller('BranchListCtrl', function($scope, $http) {
    $http.get('/branches/').success(function(data) {
        $scope.branches = data.branches;
    })
});

libraryApp.controller('BookListCtrl', function($scope, $http) {
    $http.get('/books/').success(function(data) {
        $scope.books = data.books;
    })
});

libraryApp.controller('BookSearchCtrl', function($scope, $http) {
    $scope.books = null;

    $scope.retrieve = function(book) {
        $http({
            url: '/books/',
            params: book
        }).success(function(data) {
            $scope.books = data.books;
        });
    }
});

libraryApp.controller('BookAddCtrl', function($scope, $http) {
    $scope.result = null

    $scope.add = function(book) {
        $http.post('/books/', book).success(function(data) {
            $scope.books = data.books;
        }).success(function(data, status) {
            $scope.result = {status: status, data: data};
        }).error(function(data, status) {
            $scope.result = {status: status, message: data.message};
        });
    }
});

libraryApp.controller('ReaderListCtrl', function($scope, $http) {
    $http.get('/readers/').success(function(data) {
        $scope.readers = data.readers;
    })

    $scope.selectedReader = {};

    $scope.getSelectedReaderInfo = function() {
        if (!$scope.selectedReader) {
            return;
        }
        $http.get('/readers/'+$scope.selectedReader.reader_id).success(function(data){
            $scope.selectedReaderInfo = data
        }).error(function(data) {
            $scope.selectedReaderInfo = {}
        });
    }
});

'use strict';

var libraryReaderApp = angular.module('libraryReaderApp', ['ngResource', 'angularMoment', 'ui.router', 'ui.bootstrap', 'ui.select', 'libraryUtilApp']);

var libraryUtilApp = angular.module('libraryUtilApp', []);

libraryUtilApp.filter('reservationStatus', function () {
    return function(isReserved) {
        return isReserved ? '\u2713 Active' : '\u2718 Canceled';
    }
}).filter('copyStatus', function () {
    return function(isAvailable) {
        return isAvailable ? '\u2713 Available' : '\u2718 Unavailable';
    }
});

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
    var promiseToReturn = readerIdService().then(function(reader_id) {
        return $http.get('/api/readers/'+reader_id)
    }).then(function(response) {
        return response.data
    });
    return function() {
        return promiseToReturn;
    }
}).factory('reserveInfoService', function($http, $q, readerInfoService) {
    var allPromise = [];
    var promiseToReturn = readerInfoService().then(function(reader) {
        angular.forEach(reader.reserves, function(reserve) {
            var promise = $http.get(reserve.uri).then(function(response) {
                return response.data
            });
            allPromise.push(promise)
        });

        return $q.all(allPromise);
    })

    return function() {
        return promiseToReturn;
    }
}).factory('borrowInfoService', function($http, $q, readerInfoService) {
    var allPromise = [];
    var promiseToReturn = readerInfoService().then(function(reader) {
        angular.forEach(reader.borrows, function(borrow) {
            var promise = $http.get(borrow.uri).then(function(response) {
                return response.data
            });
            allPromise.push(promise)
        });

        return $q.all(allPromise);
    })

    return function() {
        return promiseToReturn;
    }
}).factory('BooksResource', function($resource) {
    return $resource('/api/books/', {}, {
        'get': {method: 'GET'}
    })
}).factory('BookResource', function($resource) {
    return $resource('/api/books/:book_id', {}, {
        'get': {method: 'GET'}
    })
});

libraryReaderApp.controller('HomeCtrl', function($scope, reader) {
    $scope.reader = reader
}).controller('ReserveCtrl', function($scope, reserves) {
    $scope.reserves = reserves
}).controller('BorrowCtrl', function($scope, borrows) {
    $scope.borrows = borrows
}).controller('SearchCtrl', function($scope, BooksResource) {
    $scope.query = function() {
        $scope.isCollapsed = true;
        $scope.data = BooksResource.get($scope.search)
    }
}).controller('BookDetailCtrl', function($scope, $stateParams, $interval, BookResource) {
    $scope.loadData = function() {
        BookResource.get({book_id: $stateParams.bookId}).$promise.then(function (data) {
            $scope.book = data;
            $scope.hasError = false;
        }, function (errorResponse) {
            $scope.hasError = true;
        })
    };

    $scope.loadData();

    var autoUpdate = $interval($scope.loadData, 1000);

    $scope.$on('$stateChangeStart', function() {
        console.log($interval.cancel(autoUpdate))
    });
});

libraryReaderApp.config(['$resourceProvider', function($resourceProvider) {
  // Don't strip trailing slashes from calculated URLs
  $resourceProvider.defaults.stripTrailingSlashes = false;
}]).config(function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/home');

    $stateProvider.state('home', {
        url: '/home',
        templateUrl: '/partial/reader_home.html',
        resolve: {
            reader: function(readerInfoService) {
                return readerInfoService();
            }
        },
        controller: 'HomeCtrl'
    }).state('search', {
        url: '/search',
        templateUrl: '/partial/search.html',
        controller: 'SearchCtrl'
    }).state('reserves', {
        url: '/reserves',
        templateUrl: '/partial/reserves.html',
        resolve: {
            reserves: function(reserveInfoService) {
                return reserveInfoService();
            }
        },
        controller: 'ReserveCtrl'
    }).state('borrows', {
        url: '/borrows',
        templateUrl: '/partial/borrows.html',
        resolve: {
            borrows: function(borrowInfoService) {
                return borrowInfoService();
            }
        },
        controller: 'BorrowCtrl'
    }).state('bookDetail', {
        url: '/bookDetail/{bookId:int}',
        templateUrl: '/partial/book.html',
        controller: 'BookDetailCtrl'
    });
});


'use strict';

var libraryReaderApp = angular.module('libraryReaderApp', ['ngResource', 'angularMoment', 'ui.router', 'ui.bootstrap', 'ui.select', 'libraryUtilApp']);

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
    return function() {
        return readerIdService().then(function(reader_id) {
            return $http.get('/api/readers/'+reader_id)
        }).then(function(response) {
            return response.data
        });
    };
}).factory('reserveInfoService', function($http, $q, readerInfoService) {
    return function() {
        return readerInfoService().then(function(reader) {
            var allPromise = [];
            angular.forEach(reader.reserves, function(reserve) {
                var promise = $http.get(reserve.uri).then(function(response) {
                    return response.data
                });
                allPromise.push(promise);
            });
            return $q.all(allPromise);
        });
    };
}).factory('borrowInfoService', function($http, $q, readerInfoService) {
    return function() {
        return readerInfoService().then(function(reader) {
            var allPromise = [];
            angular.forEach(reader.borrows, function(borrow) {
                var promise = $http.get(borrow.uri).then(function(response) {
                    return response.data
                });
                allPromise.push(promise);
            });
            return $q.all(allPromise);
        });
    };
}).factory('BooksResource', function($resource) {
    return $resource('/api/books/', {}, {
        'get': {method: 'GET'}
    })
}).factory('BookResource', function($resource) {
    return $resource('/api/books/:book_id', {}, {
        'get': {method: 'GET'}
    })
}).factory('ReaderActionResource', function($resource) {
    return function(readerId) {
        return $resource('/api/readers/:reader_id/:verb', {}, {
            checkout: {
                method: 'POST',
                params: {
                    verb: 'checkout',
                    reader_id: readerId
                }
            },
            retrn: {
                method: 'POST',
                params: {
                    verb: 'return',
                    reader_id: readerId
                }
            },
            reserve: {
                method: 'POST',
                params: {
                    verb: 'reserve',
                    reader_id: readerId
                }
            },
            cancel: {
                method: 'POST',
                params: {
                    verb: 'cancel',
                    reader_id: readerId
                }
            }
        });
    };
});

libraryReaderApp.controller('HomeCtrl', function($scope, reader) {
    $scope.reader = reader
}).controller('ReserveCtrl', function($scope, $interval, $filter, reserves, readerId, reserveInfoService) {
    $scope.update = function(reserves) {
            $scope.activeReserves = $filter('filter')(reserves, {is_reserved: true});
            $scope.canceledReserves = $filter('filter')(reserves, {is_reserved: false});
    };
    $scope.update(reserves);
    $scope.readerId = readerId;

    $scope.loadData = function() {
        reserveInfoService().then(function (reserves) {
            $scope.update(reserves);
        });
    };

    var autoUpdate = $interval($scope.loadData, 1000);

    $scope.$on('$stateChangeStart', function() {
        $interval.cancel(autoUpdate)
    });
}).controller('ReserveCancelCtrl', function($scope, readerIdService, ReaderActionResource) {
    $scope.cancel = function() {
        ReaderActionResource($scope.readerId).cancel({
            'copy_id': $scope.reserve.copy.copy_id
        })
    };
}).controller('BorrowCtrl', function($scope, $interval, $filter, borrows, readerId, borrowInfoService) {
    $scope.update = function(borrows) {
        $scope.activeBorrow = $filter('filter')(borrows, {r_datetime: null});
        $scope.returnedBorrow = $filter('filter')(borrows, {r_datetime: '!'+null});
    };
    $scope.update(borrows);
    $scope.readerId = readerId;

    $scope.loadData = function() {
        borrowInfoService().then(function (borrows) {
            $scope.update(borrows);
        });
    };

    var autoUpdate = $interval($scope.loadData, 1000);

    $scope.$on('$stateChangeStart', function() {
        $interval.cancel(autoUpdate)
    });
}).controller('BorrowReturnCtrl', function($scope, ReaderActionResource) {
    $scope.retrn = function() {
        ReaderActionResource($scope.readerId).retrn({
            'copy_id': $scope.borrow.copy.copy_id
        });
    };
}).controller('SearchCtrl', function($scope, BooksResource) {
    $scope.query = function() {
        $scope.isCollapsed = true;
        $scope.data = BooksResource.get($scope.search)
    }
}).controller('BookDetailCtrl', function($scope, $stateParams, $interval, BookResource, readerId) {
    $scope.readerId = readerId;
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
        $interval.cancel(autoUpdate)
    });
}).controller('CopyListCtrl', function($scope, readerIdService, ReaderActionResource) {
    $scope.borrow = function() {
        ReaderActionResource($scope.readerId).checkout({
            'copy_id': $scope.copy.copy_id
        })
    };

    $scope.reserve = function() {
        ReaderActionResource($scope.readerId).reserve({
            'copy_id': $scope.copy.copy_id
        })
    };
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
        templateUrl: '/partial/search_books.html',
        controller: 'SearchCtrl'
    }).state('reserves', {
        url: '/reserves',
        templateUrl: '/partial/reserves.html',
        resolve: {
            reserves: function(reserveInfoService) {
                return reserveInfoService();
            },
            readerId: function(readerIdService) {
                return readerIdService();
            }
        },
        controller: 'ReserveCtrl'
    }).state('borrows', {
        url: '/borrows',
        templateUrl: '/partial/borrows.html',
        resolve: {
            borrows: function(borrowInfoService) {
                return borrowInfoService();
            },
            readerId: function(readerIdService) {
                return readerIdService();
            }
        },
        controller: 'BorrowCtrl'
    }).state('bookDetail', {
        url: '/bookDetail/{bookId:int}',
        templateUrl: '/partial/book.html',
        controller: 'BookDetailCtrl',
        resolve: {
            readerId: function(readerIdService) {
                return readerIdService();
            }
        }
    });
});


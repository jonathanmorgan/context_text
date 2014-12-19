angular.module( 'sourcenet_coding' ).controller("MainController", function(){
    
    // based on http://www.revillweb.com/tutorials/angularjs-in-30-minutes-angularjs-tutorial/
    var vm = this;
    vm.title = "AngularJS Tutorial Example";
    vm.searchInput = '';
    vm.shows = [
        {
            title: 'Game of Thrones',
            year: '2011',
            favorite: true
        },
        {
            title: 'Walking Dead',
            year: '2010',
            favorite: false
        },
        {
            title: 'Firefly',
            year: '2002',
            favorite: true
        },
        {
            title: 'Banshee',
            year: '2013',
            favorite: true
        },
        {
            title: 'Greys Anatomy',
            year: '2005',
            favorite: false
        }
    ];
    vm.orders = [
        {
            id: 1,
            title: 'Year Ascending',
            key: 'year',
            reverse: false
        },
        {
            id: 2,
            title: 'Year Descending',
            key: 'year',
            reverse: true
        },
        {
            id: 3,
            title: 'Title Ascending',
            key: 'title',
            reverse: false
        },
        {
            id: 4,
            title: 'Title Ascending',
            key: 'title',
            reverse: true
        }
    ];
    vm.order = vm.orders[0];
});
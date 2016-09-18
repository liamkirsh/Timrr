'use strict';

angular.module('inspinia')
  .directive('daychart', function ($window) {
    return {
      link: link,
      restrict: 'E',
      scope: {
        blocks: '='
      },
      templateUrl: 'app/components/daychart/daychart.html',

      controller:
        function (
          $scope
        ) {
          $scope.$watch("blocks", function(newValue, oldValue) {
            var blockList = [];
            var startOfPeriod = new Date();
            startOfPeriod.setDate(startOfPeriod.getDate() - 1);
            angular.forEach($scope.blocks, function(value, key) {
              var width = (new Date(value.to) - new Date(value.from)) / (24*60*60*1000) * $scope.daychartWidth;
              var left = (new Date(value.from) - startOfPeriod) / (24*60*60*1000) * $scope.daychartWidth;

              //console.log("new block");
              //console.log(Math.floor(new Date(value.from) / (24*60*60*1000)));
              //console.log(new Date(value.from));

              this.push({
                width: width,
                left: left,
                type: value.type,
                name: value.name,
                start: value.from,
                end: value.to
              });
            }, blockList);
            $scope.blockList = blockList;
          });

          // change product view and get voucher codes
          $scope.editProduct = function (product) {
            if (product === 'all') {
              $scope.currentProduct = {
                'allProducts': true
              };
            } else {
              $scope.currentProduct = product;
              ProductService.getVoucherCodes(product.id).then(function (response) {
                $scope.currentVoucherCodes = response;
              });
            }
          };

        }
    };

    function link(scope, element, attrs) {
            scope.width = $window.innerWidth;

            function getWidth() {
              return element.context.firstChild.querySelector('.daychartBar').offsetWidth;
            }
            function onResize() {
                // uncomment for only fire when $window.innerWidth change
                if (scope.width !== $window.innerWidth)
                {
                    scope.daychartWidth = getWidth();
                    scope.width = $window.innerWidth;
                    scope.$digest();
                }
            };

            function cleanUp() {
                angular.element($window).off('resize', onResize);
            }

            scope.daychartWidth = getWidth();
            angular.element($window).on('resize', onResize);
            scope.$on('$destroy', cleanUp);
            var startOfPeriod = new Date();
            startOfPeriod.setDate(startOfPeriod.getDate() - 1);

            var numberingElem = element.context.firstChild.querySelector('.daychartNumbering'); //children[1];
            var positionMultiplier = getWidth() / 24.0;
            for (var i = 0; i <= 24; i++) {
              var elem = document.createElement("div");
              var d = new Date();
              d.setHours(d.getHours() - (24 - i));
              d.setMinutes(0);
              elem.appendChild(document.createTextNode(d.getHours() + ":00"));

              elem.className = "number";
              var offset = (d - startOfPeriod) / (24*60*60*1000) * scope.daychartWidth;
              if (offset < 0) {
                  continue;
              }
              elem.style.left = offset + "px";

              numberingElem.appendChild(elem);
            }
    }
  }); 

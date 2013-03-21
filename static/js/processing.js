$(document).ready(function() {
    var listModel;
    var loaded = false;
    var $modal = $('#ajax-modal');
    
    var resultModel = function(data) {
        ko.mapping.fromJS(data, {}, this);
         
        this.resultStatus = ko.computed(function() {
            if (!this.completed()) {
                return "label-info";
            }
            
            return this.success() ? "label-success" : "label-important";
        }, this);
        
        this.id = function() {
            return this._id.$oid();
        }

        this.view =  function() {
            $('body').modalmanager('loading');
            
            $modal.load('/processing/view/' + this.id(), '', function() {
                $modal.modal();
            });
        };
    }
    
    var listMapping = {
        'results': {
            key: function(data) {
                return ko.utils.unwrapObservable(data._id.$oid);
            },
            create: function(options) {
                return new resultModel(options.data);
            }
        }
    };
    
    var reloader = function() {
       $.getJSON(window.location, function(data) {
            result = ko.mapping.fromJS(data, listMapping, listModel);            

            if (!loaded) {
                listModel = result;
                ko.applyBindings(listModel);
                loaded = true;                
            }
        
            setTimeout(reloader, 750);
       });
    };
    
    reloader();
});


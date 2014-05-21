var pageViewModel;
var resultMap = {};
var $modal;

function listViewModel() {
    var self = this;
    
    self.results = ko.observableArray();
    self.selectedRow = ko.observable();
    
    
    self.selectRow = function(row) {
        self.selectedRow(row);
        
        $('body').modalmanager('loading');
    
        $modal.load('/processing/view/' + row.id(), '', function() {
            $modal.modal();
        });        
    }
}

function resultViewModel(data) {
    var self = this;

    self.update = function(data) {
        $.each(data, function(index, value) {
            if (!self.hasOwnProperty(index)) {
                self[index] = ko.observable(value);    
            } else {
                self[index](value);
            }        
        });                
    }
    
    self.update(data);
    
    self.resultStatus = ko.computed(function() {
        if (!this.completed()) {
            return "label-info";
        }
        
        return this.success() ? "label-success" : "label-important";
    }, this);
    
    self.id = function() {
        return self._id().$oid;
    }

    resultMap[self.id()] = self;
}

$(document).ready(function() {
    pageViewModel = new listViewModel()
    var loaded = false;
    $modal = $('#ajax-modal');
    
    var reloader = function() {
       $.getJSON(window.location, function(data) {
            $.each(data.results.reverse(), function(index, value){
                _id = value._id.$oid
                if (resultMap.hasOwnProperty(_id)) {
                    resultMap[_id].update(value);
                } else {
                    pageViewModel.results.unshift(new resultViewModel(value))
                }
            });          

            if (!loaded) {
                ko.applyBindings(pageViewModel);
                loaded = true;
            }
        
            setTimeout(reloader, 2500);
       });
    };
    
    reloader();

    $modal.on('hide', function() {
        $modal.empty();
    });
});


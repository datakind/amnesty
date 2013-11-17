(function ( $ ) {

  $.fn.dynamicHighchart = function ( options , callback) {
     var chart_settings = $.extend({
        // These are the defaults.
        data_format: 'json',
        delimiter: ',',
        data: "https://premium.scraperwiki.com/cc7znvq/47d80ae900e04f2/sql/?q=SELECT * FROM t2 WHERE year = 2012 AND transaction_type = 'withdrawal' AND (month = 1 OR month = 2) AND is_total = 0",
        chart_type: 'datetime',
        series: '',
        x: 'date',
        y: 'today',
        title: 'Chart Title',
        y_axis_label: 'Y-Axis label',
        color_palette: ['#1f77b4', '#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf','#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5', '#c49c94', '#f7b6d2', '#c7c7c7', '#dbdb8d', '#9edae5'],
        min_datetick_interval: 0 // To not let the day go less than a day use 24 * 3600 * 1000
      }, options ),
      response_ds;

    String.prototype.contains = function(it) { return this.indexOf(it) != -1; };

    function commaSeparateNumber(val){
      while (/(\d+)(\d{3})/.test(val.toString())){
        val = val.toString().replace(/(\d+)(\d{3})/, '$1'+','+'$2');
      }
      return val;
    };

    function currencyFormatNumber(val){
      var with_commas = String(commaSeparateNumber(val));
      if (with_commas.contains('-')){
        return '-$' + with_commas.replace('-','');
      }else{
        return '$' + with_commas;
      };

    };

    function createAndFetchDs(chart_settings, $ctnr, json_chart_callback){
      var data_format = chart_settings.data_format,
          data        = chart_settings.data,
          delimiter   = chart_settings.delimiter;

      var miso_options = {};

      if (data_format == 'json'){
        if (typeof data == 'string'){
          miso_options = {
            url: data
          };
        }else{
          miso_options = {
            data: data
          };
        };
      }else if (data_format == 'csv'){
        miso_options = {
          url: data,
          delimiter: delimiter
        };
      }else{
        alert('Specify either "csv" or "json" for your data_format');
      };

      response_ds = new Miso.Dataset( miso_options );

      response_ds.fetch({ 
        success : function() {
          var ds = this;
          reshapeData(ds, chart_settings, $ctnr, json_chart_callback)
        },
        error : function() {
        }
      });
    };

    function reshapeData(ds, chart_settings, $ctnr, json_chart_callback){
        var items_uniq = findDistinctSeriesNames(ds, chart_settings.series), // findDistinctSeriesNames takes a miso.dataset object and the column name whose values you want unique records of. It returns an array of unique names that appear as values in the specified column.
            series_ds_arr  = geEachSeriesDs(ds, items_uniq, chart_settings.series), // getDataForEachSeries takes a miso.dataset object, the unique columns and the name of the column those unique items appear in. It returns an array of miso ds objects, one for every unique item name.
            series_data_hc = createHighChartsDataSeries(series_ds_arr, chart_settings.series, chart_settings.y, chart_settings.x, chart_settings.chart_type, chart_settings.color_palette), // createHighChartsDataSeries returns an arrray of objects that conforms to how highcharts like a series object to be, namely, a name as a string, data as an array of values and for our purposes a color chosen from the color palette index. For a datetime series, highcharts wants the data array to be an array of arrays. Each value point is an array of two values, the date in unix time and what will be the y coordinate.
            x_axis_info    = getChartTypeSpecificXAxis(chart_settings.chart_type, items_uniq, chart_settings.series, chart_settings.min_datetick_interval); // getChartTypeSpecificXAxis this will pick what kind of Highcharts xAxis object is added into the chart JSON.
        
        makeHighchart(series_data_hc, x_axis_info, chart_settings, $ctnr, json_chart_callback)
    };

    function findDistinctSeriesNames(ds, col){
      if (col != ''){
        var items = ds.column(col).data,
            items_uniq = _.uniq(items);
      }else{
        items_uniq = [''];
      };
      return items_uniq;
    };

    function geEachSeriesDs(ds, items_uniq, col){
      if (col != ''){
        var series_ds_arr = [];
        _.each(items_uniq, function(item){
          var series = ds.where({
            // copy only where the value of the specified call is equal to one of the unique item names
            rows: function(row) {
              return row[col] == item;
            }
          });
          series_ds_arr.push(series);
        })
      }else{
        series_ds_arr = [ds];
      }
      return series_ds_arr;
    };

    function keepBetweenZeroAndN(index, limit){
        var val = index - Math.floor(index / limit) * limit;
        return val;
    };

    function createHighChartsDataSeries(series_ds_arr, col, value, x, type, color_palette){
      var series = [];
      _.each(series_ds_arr, function(series_ds, index){
        var series_name = (col != '') ? series_ds.column(col).data[0] : 'data',
            series_data_value = series_ds.column(value).data,
            series_date_time,
            series_data = [];

            if (type == 'datetime'){
              series_data_time = series_ds.column(x).data;

              // Create the [unix_time, value] format that highcharts likes for time series
              for (var i = 0; i < series_data_value.length; i++){
                var date_unix = new Date(series_data_time[i]).getTime(),
                    date_val = [date_unix, series_data_value[i]];

                series_data.push(date_val)
              };
            }else{
              series_data = series_data_value;
            };

        // If you exceed the number of colors you put in, start over at the beginning.
        var color_index = keepBetweenZeroAndN(index, color_palette.length);

        var obj = {
              name:  series_name,
              color: color_palette[color_index],
              data:  series_data
            };
            series.push(obj);
      });
      return series
    }

    function getChartTypeSpecificXAxis(type, items_uniq, col, min_datetick_interval){
      var datetime = {
                  type: 'datetime',
                  minTickInterval: min_datetick_interval, 
                  dateTimeLabelFormats: {
                      millisecond: '%H:%M:%S.%L',
                      second: '%H:%M:%S',
                      minute: '%H:%M',
                      hour: '%H:%M',
                      day: '%b %e',
                      week: '%b %e',
                      month: '%b \'%y',
                      year: '%Y'
                    }
          },
          categorical = {
            categories: [col]
          },
          default_x_info = {
            tickColor: '#e3e3e3',
            lineColor: '#e3e3e3'
          };

      if (type == 'datetime'){
        return _.extend(datetime, default_x_info);
      }else{
        return _.extend(categorical, default_x_info);
      };
    };

    function makeHighchart(series_data, x_axis_info, chart_settings, $ctnr, json_chart_callback){

      Highcharts.setOptions({
        global: {
            useUTC: false
        }
      });

      $ctnr.highcharts({
          chart: {
              type: (chart_settings.chart_type == 'datetime' ? 'line' : 'column')
          },
          title: {
              text: chart_settings.title,
              style: {
                  color:'#5e5e5e',
                  font: 'normal 16px "Arial", sans-serif'
              }
          },
          subtitle: {
              text: ''
          },
          legend:{
            borderRadius: 0,
            itemHoverStyle: {
              textDecoration: 'underline'
            },
            itemStyle: {
              textDecoration: 'none'
            }
          },
          xAxis: x_axis_info,
          yAxis: {
              title: {
                  text: chart_settings.y_axis_label,
                  style: {
                    color:'#5e5e5e',
                    font: 'normal 16px "Arial", sans-serif'
                }
              },
              gridLineWidth: 1,
              gridLineColor: '#e3e3e3'
          },
          tooltip: {
              formatter: function() {
                var s = '<div class="chart-hover-title" style="color:'+ this.series.color +'">'+ this.series.name +'</div> <div class="chart-hover-info">'+
                       (chart_settings.chart_type == 'datetime' ? Highcharts.dateFormat('%b %e, %Y', this.x) : this.x) +': '+ this.y + '</div>';
                // $hover_templ.html(s).show();
                return s
              }
          },
          series: series_data,
          plotOptions: {
            line: {
              marker: {
                enabled: false,
                radius: 2
              }
            }
          }
      });
      json_chart_callback('Chart created');
      
    };


    function chartLoading($ctnr){
      $ctnr.html('<div class="chart-loading">Loading chart... <img src="data:image/gif;base64,R0lGODlhEAAQAPQAAP///wAAAPj4+Dg4OISEhAYGBiYmJtbW1qioqBYWFnZ2dmZmZuTk5JiYmMbGxkhISFZWVgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH/C05FVFNDQVBFMi4wAwEAAAAh/hpDcmVhdGVkIHdpdGggYWpheGxvYWQuaW5mbwAh+QQJCgAAACwAAAAAEAAQAAAFUCAgjmRpnqUwFGwhKoRgqq2YFMaRGjWA8AbZiIBbjQQ8AmmFUJEQhQGJhaKOrCksgEla+KIkYvC6SJKQOISoNSYdeIk1ayA8ExTyeR3F749CACH5BAkKAAAALAAAAAAQABAAAAVoICCKR9KMaCoaxeCoqEAkRX3AwMHWxQIIjJSAZWgUEgzBwCBAEQpMwIDwY1FHgwJCtOW2UDWYIDyqNVVkUbYr6CK+o2eUMKgWrqKhj0FrEM8jQQALPFA3MAc8CQSAMA5ZBjgqDQmHIyEAIfkECQoAAAAsAAAAABAAEAAABWAgII4j85Ao2hRIKgrEUBQJLaSHMe8zgQo6Q8sxS7RIhILhBkgumCTZsXkACBC+0cwF2GoLLoFXREDcDlkAojBICRaFLDCOQtQKjmsQSubtDFU/NXcDBHwkaw1cKQ8MiyEAIfkECQoAAAAsAAAAABAAEAAABVIgII5kaZ6AIJQCMRTFQKiDQx4GrBfGa4uCnAEhQuRgPwCBtwK+kCNFgjh6QlFYgGO7baJ2CxIioSDpwqNggWCGDVVGphly3BkOpXDrKfNm/4AhACH5BAkKAAAALAAAAAAQABAAAAVgICCOZGmeqEAMRTEQwskYbV0Yx7kYSIzQhtgoBxCKBDQCIOcoLBimRiFhSABYU5gIgW01pLUBYkRItAYAqrlhYiwKjiWAcDMWY8QjsCf4DewiBzQ2N1AmKlgvgCiMjSQhACH5BAkKAAAALAAAAAAQABAAAAVfICCOZGmeqEgUxUAIpkA0AMKyxkEiSZEIsJqhYAg+boUFSTAkiBiNHks3sg1ILAfBiS10gyqCg0UaFBCkwy3RYKiIYMAC+RAxiQgYsJdAjw5DN2gILzEEZgVcKYuMJiEAOwAAAAAAAAAAAA=="></div>')
    };

    function startTheShow(chart_settings, $ctnr, callback){
      chartLoading($ctnr);
      createAndFetchDs(chart_settings, $ctnr, function(response){
        callback(response); /* "Chart created" */
      });
    };

    return this.each(function(){
      var $ctnr = $(this);
      startTheShow(chart_settings, $ctnr, callback);

    });
  };

})(jQuery);

/*
  Copyright (c) 2006-2008 The Chromium Authors. All rights reserved.
  Use of this source code is governed by a BSD-style license that can be
  found in the LICENSE file.
*/

// Collection of classes used to plot data in a <canvas>.  Create a Plotter()
// to generate a plot.

// vertical marker for columns
function Marker(color) {
  var m = document.createElement("DIV");
  m.setAttribute("class", "plot-cursor");
  m.style.backgroundColor = color;
  m.style.opacity = "0.3";
  m.style.position = "absolute";
  m.style.left = "-2px";
  m.style.top = "-2px";
  m.style.width = "0px";
  m.style.height = "0px";
  return m;
}

/**
 * HorizontalMarker class
 * Create a horizontal marker at the indicated mouse location.
 * @constructor
 *
 * @param canvasRect {Object} The canvas bounds (in client coords).
 * @param clientY {Number} The vertical mouse click location that spawned
 *    the marker, in the client coordinate space.
 * @param yValue {Number} The plotted value corresponding to the clientY
 *     click location.
 */
function HorizontalMarker(canvasRect, clientY, yValue) {
  // Add a horizontal line to the graph.
  var m = document.createElement("DIV");
  m.setAttribute("class", "plot-baseline");
  m.style.backgroundColor = HorizontalMarker.COLOR;
  m.style.opacity = "0.3";
  m.style.position = "absolute";
  m.style.left = canvasRect.offsetLeft;
  var h = HorizontalMarker.HEIGHT;
  m.style.top = (clientY - h/2).toFixed(0) + "px";
  m.style.width = canvasRect.width + "px";
  m.style.height = h + "px";
  this.markerDiv_ = m;

  this.value = yValue;
}

HorizontalMarker.HEIGHT = 5;
HorizontalMarker.COLOR = "rgb(0,100,100)";

// Remove the horizontal line from the graph.
HorizontalMarker.prototype.remove_ = function() {
  this.markerDiv_.parentNode.removeChild(this.markerDiv_);
}

/**
 * Plotter class
 * @constructor
 *
 * Draws a chart using CANVAS element. Takes array of lines to draw with
 * deviations values for each data sample.
 *
 * @param {Array} clNumbers list of clNumbers for each data sample.
 * @param {Array} plotData list of arrays that represent individual lines.
 *                         The line itself is an Array of value and stdd.
 * @param {Array} dataDescription list of data description for each line
 *                         in plotData.
 * @units {string} units name of measurement used to describe plotted data.
 *
 * Example of the plotData:
 *  [
 *    [line 1 data],
 *    [line 2 data]
 *  ].
 *  Line data looks like  [[point one], [point two]].
 *  And individual points are [value, deviation value]
 */
function Plotter(clNumbers, plotData, dataDescription, units, resultNode) {
  this.clNumbers_ = clNumbers;
  this.plotData_ = plotData;
  this.dataDescription_ = dataDescription;
  this.resultNode_ = resultNode;
  this.units_ = units;
  this.coordinates = new Coordinates(plotData);

  // A color palette that's unambigous for normal and color-deficient viewers.
  // Values are (red, green, blue) on a scale of 255.
  // Taken from http://jfly.iam.u-tokyo.ac.jp/html/manuals/pdf/color_blind.pdf
  this.colors = [[0, 114, 178],   // blue
                 [230, 159, 0],   // orange
                 [0, 158, 115],   // green
                 [204, 121, 167], // purplish pink
                 [86, 180, 233],  // sky blue
                 [213, 94, 0],    // dark orange
                 [0, 0, 0],       // black
                 [240, 228, 66]   // yellow
                ];
}

/**
 * Does the actual plotting.
 */
Plotter.prototype.plot = function() {
  var canvas = this.canvas();
  this.coordinates_div_ = this.coordinates_();
  this.ruler_div_ = this.ruler();
  // marker for the result-point that the mouse is currently over
  this.cursor_div_ = new Marker("rgb(100,80,240)");
  // marker for the result-point for which details are shown
  this.marker_div_ = new Marker("rgb(100,100,100)");
  var ctx = canvas.getContext("2d");
  for (var i = 0; i < this.plotData_.length; i++)
    this.plotLine_(ctx, this.nextColor(i), this.plotData_[i]);

  this.resultNode_.appendChild(canvas);
  this.resultNode_.appendChild(this.coordinates_div_);

  this.resultNode_.appendChild(this.ruler_div_);
  this.resultNode_.appendChild(this.cursor_div_);
  this.resultNode_.appendChild(this.marker_div_);
  this.attachEventListeners(canvas);
  this.canvasRectangle = {
    "offsetLeft": canvas.offsetLeft,
    "offsetTop":  canvas.offsetTop,
    "width":      canvas.offsetWidth,
    "height":     canvas.offsetHeight
  };
};

Plotter.prototype.drawDeviationBar_ = function(context, strokeStyles, x, y,
                                                deviationValue) {
  context.strokeStyle = strokeStyles;
  context.lineWidth = 1.0;
  context.beginPath();
  context.moveTo(x, (y + deviationValue));
  context.lineTo(x, (y - deviationValue));
  context.moveTo(x, (y - deviationValue));
  context.closePath();
  context.stroke();
};

Plotter.prototype.plotLine_ = function(ctx, strokeStyles, data) {
  ctx.strokeStyle = strokeStyles;
  ctx.lineWidth = 2.0;
  ctx.beginPath();
  var initial = true;
  var deviationData = [];
  for (var i = 0; i < data.length; i++) {
    var x = this.coordinates.xPoints(i);
    var value = data[i][0];
    var stdd = data[i][1];
    var y = 0.0;
    var err = 0.0;
    if (isNaN(value)) {
      // Re-set 'initial' if we're at a gap in the data.
      initial = true;
    } else {
      y = this.coordinates.yPoints(value);
      // We assume that the stdd will only be NaN (missing) when the value is.
      if (parseFloat(value) != 0.0)
        err = y * parseFloat(stdd) / parseFloat(value);
      if (initial)
        initial = false;
      else
        ctx.lineTo(x, y);
    }

    ctx.moveTo(x, y);
    deviationData.push([x, y, err])
  }
  ctx.closePath();
  ctx.stroke();

  for (var i = 0; i < deviationData.length; i++) {
    this.drawDeviationBar_(ctx, strokeStyles, deviationData[i][0],
                            deviationData[i][1], deviationData[i][2]);
  }
};

Plotter.prototype.attachEventListeners = function(canvas) {
  var self = this;
  canvas.parentNode.addEventListener(
    "mousemove", function(evt) { self.onMouseMove_(evt); }, false);
  this.cursor_div_.addEventListener(
    "click", function(evt) { self.onMouseClick_(evt); }, false);
};

Plotter.prototype.updateRuler_ = function(evt) {
  var r = this.ruler_div_;
  r.style.left = this.canvasRectangle.offsetLeft + "px";

  r.style.top = this.canvasRectangle.offsetTop + "px";
  r.style.width = this.canvasRectangle.width + "px";
  var h = evt.clientY - this.canvasRectangle.offsetTop;
  if (h > this.canvasRectangle.height)
    h = this.canvasRectangle.height;
  r.style.height = h + "px";
};

Plotter.prototype.updateCursor_ = function() {
  var c = this.cursor_div_;
  c.style.top = this.canvasRectangle.offsetTop + "px";
  c.style.height = this.canvasRectangle.height + "px";
  var w = this.canvasRectangle.width / this.clNumbers_.length;
  var x = (this.canvasRectangle.offsetLeft +
            w * this.current_index_).toFixed(0);
  c.style.left = x + "px";
  c.style.width = w + "px";
};


Plotter.prototype.onMouseMove_ = function(evt) {
  var canvas = evt.currentTarget.firstChild;
  var positionX = evt.clientX - this.canvasRectangle.offsetLeft;
  var positionY = evt.clientY - this.canvasRectangle.offsetTop;

  this.current_index_ = this.coordinates.dataSampleIndex(positionX);
  var yValue = this.coordinates.yValue(positionY);

  this.coordinates_td_.innerHTML =
      "r" + this.clNumbers_[this.current_index_] + ": " +
      this.plotData_[0][this.current_index_][0].toFixed(2) + " " +
      this.units_ + " +/- " +
      this.plotData_[0][this.current_index_][1].toFixed(2) + " " +
      yValue.toFixed(2) + " " + this.units_;

  // If there is a horizontal marker, also display deltas relative to it.
  if (this.horizontal_marker_) {
    var baseline = this.horizontal_marker_.value;
    var delta = yValue - baseline
    var fraction = delta / baseline; // allow division by 0

    var deltaStr = (delta >= 0 ? "+" : "") + delta.toFixed(0) + " " +
        this.units_;
    var percentStr = (fraction >= 0 ? "+" : "") +
        (fraction * 100).toFixed(3) + "%";

    this.baseline_deltas_td_.innerHTML = deltaStr + ": " + percentStr;
  }

  this.updateRuler_(evt);
  this.updateCursor_();
};

Plotter.prototype.onMouseClick_ = function(evt) {
  // Shift-click controls the horizontal reference line.
  if (evt.shiftKey) {
    if (this.horizontal_marker_) {
      this.horizontal_marker_.remove_();
    }

    var canvasY = evt.clientY - this.canvasRectangle.offsetTop;
    this.horizontal_marker_ = new HorizontalMarker(this.canvasRectangle,
        evt.clientY, this.coordinates.yValue(canvasY));

    // Insert before cursor node, otherwise it catches clicks.
    this.cursor_div_.parentNode.insertBefore(
        this.horizontal_marker_.markerDiv_, this.cursor_div_);
  } else {
    var index = this.current_index_;
    var m = this.marker_div_;
    var c = this.cursor_div_;
    m.style.top = c.style.top;
    m.style.left = c.style.left;
    m.style.width = c.style.width;
    m.style.height = c.style.height;
    if ("onclick" in this) {
      var this_x = this.clNumbers_[index];
      var prev_x = index > 0 ? (parseInt(this.clNumbers_[index-1]) + 1) :
                                this_x;
      this.onclick(prev_x, this_x);
    }
  }
};

Plotter.prototype.canvas = function() {
  var canvas = document.createElement("CANVAS");
  canvas.setAttribute("id", "_canvas");
  canvas.setAttribute("class", "plot");
  canvas.setAttribute("width", this.coordinates.widthMax);
  canvas.setAttribute("height", this.coordinates.heightMax);
  return canvas;
};

Plotter.prototype.ruler = function() {
  ruler = document.createElement("DIV");
  ruler.setAttribute("class", "plot-ruler");
  ruler.style.borderBottom = "1px dotted black";
  ruler.style.position = "absolute";
  ruler.style.left = "-2px";
  ruler.style.top = "-2px";
  ruler.style.width = "0px";
  ruler.style.height = "0px";
  return ruler;
};

Plotter.prototype.coordinates_ = function() {
  var coordinatesDiv = document.createElement("DIV");
  var table_html =
     "<table border=0 width='100%'><tbody><tr>" +
     "<td colspan=2 class='legend'>Legend: ";
  for (var i = 0; i < this.dataDescription_.length; i++) {
    if (i > 0)
      table_html += ", ";
    table_html += "<span class='legend_item' style='color:" +
      this.nextColor(i) + "'>" + this.dataDescription_[i] + "</span>";
  }
  table_html += "</td></tr><tr>" +
     "<td class='plot-coordinates'><i>move mouse over graph</i></td>" +
     "<td align=right style='color: " + HorizontalMarker.COLOR +
     "'><i>Shift-click to place baseline</i></td>" +
     "</tr></tbody></table>";
  coordinatesDiv.innerHTML = table_html;

  var tr = coordinatesDiv.firstChild.firstChild.childNodes[1];
  this.coordinates_td_ = tr.childNodes[0];
  this.baseline_deltas_td_ = tr.childNodes[1];

  return coordinatesDiv;
};

Plotter.prototype.nextColor = function(i) {
  var index = i % this.colors.length;
  return "rgb(" + this.colors[index][0] + "," +
                  this.colors[index][1] + "," +
                  this.colors[index][2] + ")";
};

Plotter.prototype.log = function(val) {
  document.getElementById('log').appendChild(
    document.createTextNode(val + '\n'));
};

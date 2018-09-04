import datetime
import xml.sax
import os
import json
from file_manager import (
    GeojsonFileManager,
    ErrorsFileManager,
    GeopointsFileManager
)


class FeatureCompletenessParser(xml.sax.ContentHandler):

    def __init__(self, required_tags, render_data_path):
        xml.sax.ContentHandler.__init__(self)
        self.required_tags = required_tags
        
        self.is_element = False
        self.has_tags = False
        self.tags = {}
        self.features_collected = 0 # element has tags
        self.features_completed = 0 # element has no errors
        self.errors_warnings = 0
        self.unused_nodes = {}
        self.geojson_file_manager = GeojsonFileManager(
            destination=render_data_path)
        self.errors_file_manager = ErrorsFileManager(
            destination=render_data_path)
        self.geopoints_file_manager = GeopointsFileManager(
            destination=render_data_path)

    def startDocument(self):
        return

    def endDocument(self):
        self.geojson_file_manager.close()
        self.geojson_file_manager.save()
        
        self.errors_file_manager.close()
        self.errors_file_manager.save()

        self.geopoints_file_manager.close()
        self.geopoints_file_manager.save()


    def startElement(self, name, attrs):
        if name in ['node', 'way', 'relation']:
            self.build_element(name, attrs)
            self.is_element = True
            self.has_tags = False
            self.element_complete = True

        if self.is_element == True:
            if name == 'tag':
                self.has_tags = True
                self.tags[attrs.getValue('k')] = attrs.getValue('v')
            elif name == 'nd':
                self.has_tags = False

        if self.is_element and self.element['type'] == 'way':
            if name == 'nd':
                ref = attrs.getValue('ref')
                if ref in self.unused_nodes:
                    self.element['nodes'].append(self.unused_nodes[ref])

    def endElement(self, name):
        if name in ['node', 'way', 'relation']:
            if self.has_tags == True:
                self.features_collected += 1
                self.check_errors_in_tags()
                self.check_warnings_in_tags()
                if self.element_complete:
                    self.features_completed += 1
        if name == 'node':
            if self.has_tags == True:            
                self.build_feature('node')
                self.build_point('node')
                self.tags = {}
            elif self.has_tags == False:
                self.unused_nodes[self.element['id']] = [
                    float(self.element['lon']), 
                    float(self.element['lat'])
                ]
        if name == 'way':
            self.build_feature('way')
            self.build_point('way')
            self.tags = {}

    def build_element(self, name, attrs):
        self.element = {
            'id': attrs.getValue("id"),
            'type': name,
            'timestamp': attrs.getValue("timestamp"),
            'nodes': []
        }
        if name == 'node':
            self.element['lon'] = attrs.getValue("lon")
            self.element['lat'] = attrs.getValue("lat")

    def check_errors_in_tags(self):
        errors = []
        self.errors_to_s = None
        for (key, values) in self.required_tags.items():
            if key not in self.tags.keys():
                error = '{key} not found'.format(key=key)
                errors.append(error)
            else:
                if len(values) > 0 and self.tags[key] not in values:
                    error = '{value} not allowed for value {key}'.format(
                        value=self.tags[key],
                        key=key)
                    errors.append(error)

        if len(errors) > 0:
            self.element_complete = False
            self.errors_to_s = ', '.join(errors)
            self.build_error_warning('error', self.errors_to_s)

        self.completeness_pct = int(100 - \
            (len(errors) / len(self.required_tags) * 100))

    def check_warnings_in_tags(self):
        warnings = []
        self.warnings_to_s = None
        if 'name' in self.tags:
            name = self.tags['name']
            if name.isupper():
                self.element_complete = False
                warning = '{name} is all uppercase'.format(
                    name=name)
                warnings.append(warning)
                
            elif name.islower():
                self.element_complete = False
                warning = '{name} is all lowercase'.format(
                    name=name)
                warnings.append(warning)
            # else:
                # mixed case
        if len(warnings) > 0:
            self.element_complete = False
            self.warnings_to_s = ', '.join(warnings)
            self.build_error_warning('warning', self.warnings_to_s)

    def build_error_warning(self, type, content):
        payload = {
            'status': type,
            'type': self.element['type'],
            'id': self.element['id'],
            'date': self.element['timestamp'],
            'comment': content
        }
        self.errors_file_manager.write(json.dumps(payload))
        self.errors_warnings += 1

    def build_point(self, osm_type):
        if osm_type == 'node':
            point = [
                float(self.element['lat']),
                float(self.element['lon']),
                self.set_color_completeness(),
                self.build_popup()
            ]
            self.geopoints_file_manager.write(json.dumps(point))


    def build_feature(self, osm_type):
        if osm_type == 'node':
            geo_type = 'Point'
            coordinates = [
               float(self.element['lon']), 
                float(self.element['lat'])
            ]
        elif osm_type == 'way':
            geo_type = 'Polygon'
            coordinates = [
               self.element['nodes']
            ]

        feature = {
            "type": "Feature",
            "geometry": {
                "type": geo_type,
                "coordinates": coordinates
            },
            "properties": {
                # "type": self.element['type'],
                # "tags": self.tags,
                # "errors": self.errors_to_s,
                # "warnings": self.warnings_to_s,
                "completeness_color": self.set_color_completeness(),
                # "completeness_pct": '{pct}%'.format(pct=self.completeness_pct),
                "popup": self.build_popup()
            },
            "id": self.element['id'],
        }
        self.geojson_file_manager.write(json.dumps(feature))

    def build_popup(self):
        link = "".join([
            "<a href=\"{root}/{type}/{id}\" target=\"_blank\">",
            "{root}/{type}/{id}</a>"]).format(
                root="https://www.openstreetmap.org",
                type=self.element['type'],
                id=self.element['id'])

        content = "{link}<br />".format(link=link);

        el_type = "<b>type</b> : {type}".format(type=self.element['type'])
        content += "{el_type}<br />".format(el_type=el_type)

        if self.errors_to_s != None:
            errors = "<div style='color:red'><b>errors</b> : {errors}</div>".format(
                errors=self.errors_to_s)
            content += errors;

        if self.warnings_to_s != None:
            warnings = "<div style='color:orange'><b>warnings</b> : {warnings}</div>".format(
                warnings=self.warnings_to_s)
            content += warnings;

        tags = []
        for tag in self.tags.items():
            tag_to_s = "<b>{tag_key}</b> : {tag_value}".format(
                tag_key=tag[0],
                tag_value=tag[1])
            tags.append(tag_to_s)

        tags = "<br />".join(tags)
  
        content += "{tags}<br />".format(tags=tags)
    
        percentage = "<b>completeness</b> : {completeness_pct}%".format(
            completeness_pct=self.completeness_pct)

        content += percentage;

        return content

    def set_color_completeness(self):
        if self.completeness_pct == 100:
            return '#00840d';
        if self.completeness_pct >= 75:
            return '#faff00';
        if self.completeness_pct >= 50:
            return '#ffe500';
        if self.completeness_pct >= 25:
            return '#FD9A08';
        if self.completeness_pct >= 0:
            return '#ff0000';

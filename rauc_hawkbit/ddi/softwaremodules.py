# -*- coding: utf-8 -*-

class FileName(object):
    """
    Represents /{tenant}/controller/v1/{targetid}/softwaremodules/{softwareModuleId}/artifacts/{fileName} # noqa
    in HawkBit's DDI API.
    """
    def __init__(self, ddi, software_module_id, file_name):
        self.ddi = ddi
        self.software_module_id = software_module_id
        self.file_name = file_name

    async def __call__(self, bundle_dl_location):
        """
        See http://sp.apps.bosch-iot-cloud.com/documentation/rest-api/rootcontroller-api-guide.html#_get_tenant_controller_v1_targetid_softwaremodules_softwaremoduleid_artifacts_filename # noqa
        """
        return await self.ddi.get_binary_resource(
            '/{tenant}/controller/v1/{controllerId}/softwaremodules/{moduleId}/artifacts/{filename}', bundle_dl_location, moduleId=self.software_module_id,
            filename=self.file_name)

    async def MD5SUM(self, md5_dl_location):
        """
        See http://sp.apps.bosch-iot-cloud.com/documentation/rest-api/rootcontroller-api-guide.html#_get_tenant_controller_v1_targetid_softwaremodules_softwaremoduleid_artifacts_filename_md5sum # noqa
        """
        return await self.ddi.get_binary_resource(
            '/{tenant}/controller/v1/{controllerId}/softwaremodules/{moduleId}/artifacts/{filename}', md5_dl_location, mime='text/plain', moduleId=self.software_module_id,
            filename=self.file_name)


class Artifacts(object):
    """
    Represents /{tenant}/controller/v1/{targetid}/softwaremodules/{softwareModuleId}/artifacts # noqa
    in HawkBit's DDI API.
    """
    def __init__(self, ddi, software_module_id):
        self.ddi = ddi
        self.software_module_id = software_module_id

    async def __call__(self):
        """
        See http://sp.apps.bosch-iot-cloud.com/documentation/rest-api/rootcontroller-api-guide.html#_get_tenant_controller_v1_targetid_softwaremodules_softwaremoduleid_artifacts # noqa
        """
        return await self.ddi.get_resource(
            '/{tenant}/controller/v1/{controllerId}/softwaremodules/{moduleId}/artifacts', moduleId=self.software_module_id)

    def __getitem__(self, key):
        filename = key
        return FileName(self.ddi, self.software_module_id, filename)


class SoftwareModule(object):
    """
    Represents /{tenant}/controller/v1/{targetid}/softwaremodules/{softwareModuleId} # noqa
    in HawkBit's DDI API.
    """
    def __init__(self, ddi, software_module_id):
        self.ddi = ddi
        self.software_module_id = software_module_id

    @property
    def artifacts(self):
        return Artifacts(self.ddi, self.software_module_id)


class SoftwareModules(object):
    """
    Represents /{tenant}/controller/v1/{targetid}/softwaremodules in
    HawkBit's DDI API.
    """
    def __init__(self, ddi):
        self.ddi = ddi

    def __getitem__(self, software_module_id):
        return SoftwareModule(self.ddi, software_module_id)

# -*- coding: utf-8 -*-

import asyncio
from gi.repository import Gio
import logging
import traceback


class DBUSException(Exception):
    pass


class AsyncDBUSClient(object):
    def __init__(self):
        self.logger = logging.getLogger('rauc_hawkbit')
        self.dbus_events = asyncio.Queue()
        loop = asyncio.get_event_loop()
        # handle dbus events in async way
        self.dbus_event_task = loop.create_task(self.handle_dbus_event())
        # holds active subscriptions
        self.signal_subscriptions = []
        # ({interface}, {signal}): {callback}
        self.signal_callbacks = {}
        # ({interface}, {property}): {callback}
        self.property_callbacks = {}

        self.system_bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)

        # always subscribe to property changes by default
        self.new_signal_subscription('org.freedesktop.DBus.Properties',
                                     'PropertiesChanged',
                                     self.property_changed_callback)

    def __del__(self):
        self.cleanup_dbus()

    def cleanup_dbus(self):
        """Unsubscribe on deletion."""
        for subscription in self.signal_subscriptions:
            self.system_bus.signal_unsubscribe(subscription)

        self.dbus_event_task.cancel()

    def on_dbus_event(self, *args):
        """Generic sync callback for all DBUS events."""
        self.dbus_events.put_nowait(args)

    async def handle_dbus_event(self):
        """
        Retrieves DBUS events from queue and calls corresponding async
        callback.
        """
        while True:
            try:
                event = await self.dbus_events.get()
                interface = event[3]
                signal = event[4]
                await self.signal_callbacks[(interface, signal)](*event)
            except Exception as e:
                traceback.print_exc()
                self.logger.error(str(e))

    def new_proxy(self, interface, object_path):
        """Returns a new managed proxy."""
        # assume name is interface without last part
        name = '.'.join(interface.split('.')[:-1])
        proxy = Gio.DBusProxy.new_sync(self.system_bus, 0, None, name,
                                       object_path, interface, None)

        # FIXME: check for methods
        if len(proxy.get_cached_property_names()) == 0:
            self.logger.warning('Proxy {} contains no properties')

        return proxy

    def new_signal_subscription(self, interface, signal, callback):
        """Add new signal subscription."""
        signal_subscription = self.system_bus.signal_subscribe(
            None, interface, signal, None, None, 0, self.on_dbus_event)
        self.signal_callbacks[(interface, signal)] = callback
        self.signal_subscriptions.append(signal_subscription)

    def new_property_subscription(self, interface, property_, callback):
        """Add new property subscription."""
        self.property_callbacks[(interface, property_)] = callback

    async def property_changed_callback(self, connection, sender_name,
                                        object_path, interface_name,
                                        signal_name, parameters):
        """
        Callback for changed properties. Calls callbacks for changed
        properties as if they were signals.
        """
        property_interface = parameters[0]

        changed_properties = {k: v for k, v in parameters[1].items()
                              if (property_interface, k) in
                              self.property_callbacks}

        for attribute, status in changed_properties.items():
            await self.property_callbacks[(property_interface, attribute)](
                connection, sender_name, object_path, property_interface,
                attribute, status)

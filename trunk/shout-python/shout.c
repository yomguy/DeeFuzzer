/* shout.c: python bindings to libshout
 * Copyright (c) 2003,5 Brendan Cully <brendan@xiph.org>
 *
 *  This library is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU Library General Public
 *  License as published by the Free Software Foundation; either
 *  version 2 of the License, or (at your option) any later version.
 *
 *  This library is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *  Library General Public License for more details.
 *
 *  You should have received a copy of the GNU Library General Public
 *  License along with this library; if not, write to the 
 *  Free Software Foundation, Inc., 59 Temple Place - Suite 330, 
 *  Boston, MA  02111-1307  USA.
 *
 * $Id$
 */

#include <Python.h>
#include <shout/shout.h>

static PyObject* ShoutError;

typedef struct {
  PyObject_HEAD
  shout_t* conn;
  PyObject* attr;
} ShoutObject;

typedef int(*pshout_set_shout)(shout_t*);
typedef int(*pshout_set_shout_int)(shout_t*, int);
typedef int(*pshout_set_shout_str)(shout_t*, const char*);

typedef struct _ShoutObjectAttr {
  const char* name;
  pshout_set_shout set_shout;
  int(*set)(struct _ShoutObjectAttr*, ShoutObject*, PyObject*);
} ShoutObjectAttr;

typedef struct {
  const char* name;
  int val;
} kv_strint;

/* -- module prototypes -- */
static PyObject* pshout_version(PyObject* self, PyObject* args);

/* -- ShoutObject instance prototypes -- */
static PyObject* pshoutobj_new(PyObject* self, PyObject* args);
static void pshoutobj_initattrs(PyObject* self);
static void pshoutobj_free(PyObject* self);
static PyObject* pshoutobj_getattr(PyObject* self, char* name);
static int pshoutobj_setattr(PyObject* self, char* name, PyObject* v);

static PyObject* pshoutobj_open(ShoutObject* self);
static PyObject* pshoutobj_close(ShoutObject* self);
static PyObject* pshoutobj_get_connected(ShoutObject* self);
static PyObject* pshoutobj_send(ShoutObject* self, PyObject* args);
static PyObject* pshoutobj_sync(ShoutObject* self);
static PyObject* pshoutobj_delay(ShoutObject* self);
static PyObject* pshoutobj_queuelen(ShoutObject* self);
static PyObject* pshoutobj_set_metadata(ShoutObject* self, PyObject* args);

/* -- attr prototypes -- */
static int pshoutobj_set_str(ShoutObjectAttr* attr, ShoutObject* self, PyObject* v);
static int pshoutobj_set_int(ShoutObjectAttr* attr, ShoutObject* self, PyObject* v);
static int pshoutobj_set_bool(ShoutObjectAttr* attr, ShoutObject* self, PyObject* v);
static int pshoutobj_set_proto(ShoutObjectAttr* attr, ShoutObject* self, PyObject* v);
static int pshoutobj_set_fmt(ShoutObjectAttr* attr, ShoutObject* self, PyObject* v);
static int pshoutobj_set_audio_info(ShoutObjectAttr* attr, ShoutObject* self, PyObject* v);

static char docstring[] = "Shout library v2 interface\n\n"
  "Use this module to send audio data to an icecast (or shoutcast) server\n"
  "shout.Shout() creates a new Shout object.\n\n"

  "Shout\n\n"
  "Use this object to send data to an icecast server.\n"
  "Set the connection attributes before calling \"open\" (at least\n"
  "\"host\", \"port\", \"password\" and \"mount\" must be specified).\n\n"
  "Methods:\n"
  "            open() - connect to server\n"
  "   get_connected() - monitor connection status in nonblocking mode\n"
  "           close() - disconnect from server\n"
  "        send(data) - send audio data to server\n"
  "            sync() - sleep until server needs more data. This is equal to\n"
  "                     the time it takes to play data sent since last sync\n"
  "           delay() - return milliseconds to wait before sending more data\n"
  "        queuelen() - return number of bytes on the nonblocking write queue\n"
  "set_metadata(dict) - update stream metadata on server (current known key is\n"
  "                     \"song\". Not currently supported for ogg.\n\n"
  "Attributes:\n"
  "       host - name or address of destination server\n"
  "       port - port of destination server\n"
  "       user - source user name (optional)\n"
  "   password - source password\n"
  "      mount - mount point on server (relative URL, eg \"/stream.ogg\")\n"
  "   protocol - server protocol: \"http\" (the default) for icecast 2,\n"
  "              \"xaudiocast\" for icecast 1, or \"icy\" for shoutcast\n"
  "nonblocking - use nonblocking send\n"
  "     format - audio format: \"ogg\" (the default) or \"mp3\"\n"
  "       name - stream name\n"
  "        url - stream web page\n"
  "      genre - stream genre\n"
  "description - longer stream description\n"
  " audio_info - dictionary of stream audio parameters, for YP information.\n"
  "              Useful keys include \"bitrate\" (in kbps), \"samplerate\"\n"
  "              (in Hz), \"channels\" and \"quality\" (Ogg encoding\n"
  "              quality). All dictionary values should be strings. The known\n"
  "              keys are defined as the SHOUT_AI_* constants, but any other\n"
  "              will be passed along to the server as well.\n"
  "   dumpfile - file name to record stream to on server (not supported on\n"
  "              all servers)\n"
  "      agent - for customizing the HTTP user-agent header\n\n";

static PyTypeObject ShoutObject_Type = {
  PyObject_HEAD_INIT(NULL)
  0,
  "shout.Shout",
  sizeof(ShoutObject),
  0,
  pshoutobj_free, /* tp_dealloc */
  0,           /* tp_print */
  pshoutobj_getattr,
  pshoutobj_setattr,
  0,           /* tp_compare */
  0,           /* tp_repr */
  0,           /* tp_as_number */
  0,           /* tp_as_sequence */
  0,           /* tp_as_mapping */
  0,           /* tp_hash */
  0,           /* tp_call */
  0,           /* tp_str */
  0,           /* tp_getattro */
  0,           /* tp_setattro */
  0,           /* tp_as_buffer */
  0,           /* tp_flags */
  "See shout module help: help(shout)\n"
};

static PyMethodDef ShoutMethods[] = {
  { "version", pshout_version, METH_VARARGS,
    "Return the version of libshout being used, as a string." },
  { "Shout", pshoutobj_new, METH_VARARGS,
    "Create a new Shout object." },
  { NULL, NULL, 0, NULL }
};

static ShoutObjectAttr ShoutObjectAttrs[] = {
  { "host",        (pshout_set_shout)shout_set_host, pshoutobj_set_str },
  { "port",        (pshout_set_shout)shout_set_port, pshoutobj_set_int },
  { "user",        (pshout_set_shout)shout_set_user, pshoutobj_set_str },
  { "password",    (pshout_set_shout)shout_set_password, pshoutobj_set_str },
  { "agent",       (pshout_set_shout)shout_set_agent, pshoutobj_set_str },
  { "format",      (pshout_set_shout)shout_set_format, pshoutobj_set_fmt },
  { "protocol",    (pshout_set_shout)shout_set_protocol, pshoutobj_set_proto },
  { "nonblocking", (pshout_set_shout)shout_set_nonblocking, pshoutobj_set_bool },
  { "mount",       (pshout_set_shout)shout_set_mount, pshoutobj_set_str },
  { "name",        (pshout_set_shout)shout_set_name, pshoutobj_set_str },
  { "url",         (pshout_set_shout)shout_set_url, pshoutobj_set_str },
  { "genre",       (pshout_set_shout)shout_set_genre, pshoutobj_set_str },
  { "description", (pshout_set_shout)shout_set_description, pshoutobj_set_str },
  { "public",      (pshout_set_shout)shout_set_public, pshoutobj_set_int },
  { "dumpfile",    (pshout_set_shout)shout_set_dumpfile, pshoutobj_set_str },
  { "audio_info",  NULL, pshoutobj_set_audio_info },
  { NULL, NULL, NULL }
};

static kv_strint ShoutProtocolMap[] = {
  { "http",       SHOUT_PROTOCOL_HTTP },
  { "xaudiocast", SHOUT_PROTOCOL_XAUDIOCAST },
  { "icy",        SHOUT_PROTOCOL_ICY },
  { NULL, 0 }
};

static kv_strint ShoutFormatMap[] = {
  { "ogg",    SHOUT_FORMAT_OGG },
  { "mp3",    SHOUT_FORMAT_MP3 },
  { "vorbis", SHOUT_FORMAT_OGG }, /* for backwards compatability */
  { NULL, 0 }
};

static PyMethodDef ShoutObjectMethods[] = {
  { "open", (PyCFunction)pshoutobj_open, METH_NOARGS,
    "Connect to server." },
  { "close", (PyCFunction)pshoutobj_close, METH_NOARGS,
    "Close connection to server." },
  { "get_connected", (PyCFunction)pshoutobj_get_connected, METH_NOARGS,
    "Check for connection progress." },
  { "send", (PyCFunction)pshoutobj_send, METH_VARARGS,
    "Send audio data to server." },
  { "sync", (PyCFunction)pshoutobj_sync, METH_NOARGS,
    "Sleep for time required to play previously sent audio data." },
  { "delay", (PyCFunction)pshoutobj_delay, METH_NOARGS,
    "Return amount of time in milliseconds to wait before sending more data." },
  { "queuelen", (PyCFunction)pshoutobj_queuelen, METH_NOARGS,
    "Return the number of bytes currently on the write queue for nonblocking send" },
  { "set_metadata", (PyCFunction)pshoutobj_set_metadata, METH_VARARGS,
    "Update stream metadata on server (takes a dictionary argument. Current keys are: \"song\"" },

  /* attributes (cribbed from Arc's ogg-python technique) */
  { "host", NULL, 0, NULL },
  { "port", NULL, 0, NULL },
  { "user", NULL, 0, NULL },
  { "password", NULL, 0, NULL },
  { "agent", NULL, 0, NULL },
  { "format", NULL, 0, NULL },
  { "protocol", NULL, 0, NULL },
  { "nonblocking", NULL, 0, NULL },
  { "mount", NULL, 0, NULL },
  { "name", NULL, 0, NULL },
  { "url", NULL, 0, NULL },
  { "genre", NULL, 0, NULL },
  { "description", NULL, 0, NULL },
  { "public", NULL, 0, NULL },
  { "dumpfile", NULL, 0, NULL },
  { "audio_info", NULL, 0, NULL },
  
  /* sentinel */
  { NULL, NULL, 0, NULL }
};

void initshout(void) {
  PyObject* mod;
  PyObject* dict;

  ShoutObject_Type.ob_type = &PyType_Type;

  mod = Py_InitModule3("shout", ShoutMethods, docstring);
  dict = PyModule_GetDict(mod);
  ShoutError = PyErr_NewException("shout.ShoutException", NULL, NULL);
  PyDict_SetItemString(dict, "ShoutException", ShoutError);

  PyModule_AddIntConstant(mod, "SHOUTERR_SUCCESS", SHOUTERR_SUCCESS);
  PyModule_AddIntConstant(mod, "SHOUTERR_INSANE", SHOUTERR_INSANE);
  PyModule_AddIntConstant(mod, "SHOUTERR_NOCONNECT", SHOUTERR_NOCONNECT);
  PyModule_AddIntConstant(mod, "SHOUTERR_NOLOGIN", SHOUTERR_NOLOGIN);
  PyModule_AddIntConstant(mod, "SHOUTERR_SOCKET", SHOUTERR_SOCKET);
  PyModule_AddIntConstant(mod, "SHOUTERR_MALLOC", SHOUTERR_MALLOC);
  PyModule_AddIntConstant(mod, "SHOUTERR_METADATA", SHOUTERR_METADATA);
  PyModule_AddIntConstant(mod, "SHOUTERR_CONNECTED", SHOUTERR_CONNECTED);
  PyModule_AddIntConstant(mod, "SHOUTERR_UNCONNECTED", SHOUTERR_UNCONNECTED);
  PyModule_AddIntConstant(mod, "SHOUTERR_UNSUPPORTED", SHOUTERR_UNSUPPORTED);
  PyModule_AddIntConstant(mod, "SHOUTERR_BUSY", SHOUTERR_BUSY);

  PyModule_AddStringConstant(mod, "SHOUT_AI_BITRATE", SHOUT_AI_BITRATE);
  PyModule_AddStringConstant(mod, "SHOUT_AI_SAMPLERATE", SHOUT_AI_SAMPLERATE);
  PyModule_AddStringConstant(mod, "SHOUT_AI_CHANNELS", SHOUT_AI_CHANNELS);
  PyModule_AddStringConstant(mod, "SHOUT_AI_QUALITY", SHOUT_AI_QUALITY);
}

/* -- shout module methods -- */

static PyObject* pshout_version(PyObject* self, PyObject* args) {
  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  return Py_BuildValue("s", shout_version(NULL, NULL, NULL));
}

/* -- ShoutObject instance methods -- */

static PyObject* pshoutobj_new(PyObject* self, PyObject* args) {
  ShoutObject* me;

  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  if (!(me = PyObject_New(ShoutObject, &ShoutObject_Type)))
    return NULL;

  me->attr = NULL;

  if (!(me->conn = shout_new())) {
    PyErr_NoMemory();
    PyObject_Del(self);

    return NULL;
  }

  return (PyObject*)me;
}

static void pshoutobj_free(PyObject* self) {
  ShoutObject* me = (ShoutObject*)self;

  Py_XDECREF(me->attr);
  shout_free(me->conn);
  PyObject_Del(self);
}

static void pshoutobj_initattrs(PyObject* self) {
  shout_t* conn = ((ShoutObject*)self)->conn;
  int val, i;

  pshoutobj_setattr(self, "host", Py_BuildValue("s", shout_get_host(conn)));
  pshoutobj_setattr(self, "port", Py_BuildValue("i", shout_get_port(conn)));
  pshoutobj_setattr(self, "user", Py_BuildValue("s", shout_get_user(conn)));
  pshoutobj_setattr(self, "password", Py_BuildValue(""));
  pshoutobj_setattr(self, "mount", Py_BuildValue(""));
  pshoutobj_setattr(self, "name", Py_BuildValue(""));
  pshoutobj_setattr(self, "url", Py_BuildValue(""));
  pshoutobj_setattr(self, "genre", Py_BuildValue(""));
  pshoutobj_setattr(self, "description", Py_BuildValue(""));
  pshoutobj_setattr(self, "audio_info", Py_BuildValue(""));
  pshoutobj_setattr(self, "dumpfile", Py_BuildValue(""));  
  pshoutobj_setattr(self, "agent", Py_BuildValue("s", shout_get_agent(conn)));
  pshoutobj_setattr(self, "protocol", Py_BuildValue(""));
  pshoutobj_setattr(self, "nonblocking", shout_get_nonblocking(conn) ? Py_True : Py_False);
  pshoutobj_setattr(self, "format", Py_BuildValue(""));

  val = shout_get_protocol(conn);
  for (i = 0; ShoutProtocolMap[i].name; i++)
    if (ShoutProtocolMap[i].val == val) {
      pshoutobj_setattr(self, "protocol", Py_BuildValue("s", ShoutProtocolMap[i].name));
      break;
    }

  val = shout_get_format(conn);
  for (i = 0; ShoutFormatMap[i].name; i++)
    if (ShoutFormatMap[i].val == val) {
      pshoutobj_setattr(self, "format", Py_BuildValue("s", ShoutFormatMap[i].name));
      break;
    }
}

static PyObject* pshoutobj_getattr(PyObject* self, char* name) {
  ShoutObject* me = (ShoutObject*)self;

  if (!me->attr)
    pshoutobj_initattrs(self);

  if (me->attr) {
    PyObject* v = PyDict_GetItemString(me->attr, name);
    if (v) {
      Py_INCREF(v);
      return v;
    }
  }
  return Py_FindMethod(ShoutObjectMethods, self, name);
}

static int pshoutobj_setattr(PyObject* self, char* name, PyObject* v) {
  ShoutObject* me = (ShoutObject*)self;
  ShoutObjectAttr* attr;

  if (!me->attr && !(me->attr = PyDict_New()))
    return -1;

  if (v == NULL)
    return -1;
  
  for (attr = ShoutObjectAttrs; attr->name; attr++) {
    if (!strcmp(attr->name, name)) {
      if (v != Py_None && attr->set(attr, me, v) != SHOUTERR_SUCCESS) {
	if (!PyErr_Occurred())
	  PyErr_SetString(ShoutError, shout_get_error(me->conn));
        return -1;
      }
      break;
    }
  }

  return PyDict_SetItemString(me->attr, name, v);
}

static PyObject* pshoutobj_open(ShoutObject* self) {
  int ret;
  Py_BEGIN_ALLOW_THREADS
  ret=shout_open(self->conn);
  Py_END_ALLOW_THREADS
  if (!((ret == SHOUTERR_SUCCESS)||
        ((ret==SHOUTERR_BUSY) && shout_get_nonblocking(self->conn)))) {
    PyErr_SetString(ShoutError, shout_get_error(self->conn));
    
    return NULL;
  }

  return Py_BuildValue("i", 1);
}

static PyObject* pshoutobj_close(ShoutObject* self) {
  if (shout_close(self->conn) != SHOUTERR_SUCCESS) {
    PyErr_SetString(ShoutError, shout_get_error(self->conn));

    return NULL;
  }

  return Py_BuildValue("i", 1);
}

static PyObject* pshoutobj_send(ShoutObject* self, PyObject* args) {
  const unsigned char* data;
  size_t len;
  int res;

  if (!PyArg_ParseTuple(args, "s#", &data, &len))
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  res = shout_send(self->conn, data, len);
  Py_END_ALLOW_THREADS

  if (res != SHOUTERR_SUCCESS) { 
    PyErr_SetString(ShoutError, shout_get_error(self->conn));

    return NULL;
  }

  return Py_BuildValue("i", 1);
}

static PyObject* pshoutobj_sync(ShoutObject* self) {
  Py_BEGIN_ALLOW_THREADS
  shout_sync(self->conn);
  Py_END_ALLOW_THREADS

  return Py_BuildValue("i", 1);
}

static PyObject* pshoutobj_get_connected(ShoutObject* self) {
  return Py_BuildValue("i", shout_get_connected(self->conn));
}

static PyObject* pshoutobj_delay(ShoutObject* self) {
  return Py_BuildValue("i", shout_delay(self->conn));
}

static PyObject* pshoutobj_queuelen(ShoutObject* self) {
  return Py_BuildValue("i", shout_queuelen(self->conn));
}

static PyObject* pshoutobj_set_metadata(ShoutObject* self, PyObject* args) {
  shout_metadata_t* metadata;
  PyObject* dict;
  PyObject* key;
  PyObject* val;
  const char* skey;
  const char* sval;
  Py_ssize_t i = 0;
  int rc;

  if (!(metadata = shout_metadata_new())) {
    PyErr_NoMemory();
    return NULL;
  }

  if (!PyArg_ParseTuple(args, "O!", &PyDict_Type, &dict))
    return NULL;

  while (PyDict_Next(dict, &i, &key, &val)) {
    if (!PyString_Check(key)) {
      PyErr_SetString(PyExc_TypeError, "Dictionary key must be string");
      shout_metadata_free(metadata);
      return NULL;
    }
    if (!PyString_Check(val)) {
      PyErr_SetString(PyExc_TypeError, "Dictionary value must be string");
      shout_metadata_free(metadata);
      return NULL;
    }

    skey = PyString_AsString(key);
    sval = PyString_AsString(val);

    if ((rc = shout_metadata_add(metadata, skey, sval)) != SHOUTERR_SUCCESS) {
      if (rc == SHOUTERR_MALLOC)
	PyErr_NoMemory();
      else if (rc == SHOUTERR_INSANE)
	PyErr_SetString(PyExc_TypeError, "Dictionary key must not be empty");
      shout_metadata_free(metadata);
      return NULL;
    }
  }

  rc = shout_set_metadata(self->conn, metadata);
  shout_metadata_free(metadata);

  if (rc != SHOUTERR_SUCCESS) {
    PyErr_SetString(ShoutError, "Metadata not supported in this connection");
    return NULL;
  }

  return Py_BuildValue("i", 1);
}

static int pshoutobj_set_str(ShoutObjectAttr* attr, ShoutObject* self, PyObject* v) {
  const char* str;
  pshout_set_shout_str set_shout;

  if (!PyString_Check(v)) {
    PyErr_SetString(PyExc_TypeError, "String argument required");
    return -1;
  }

  str = PyString_AsString(v);
  set_shout = (pshout_set_shout_str)attr->set_shout;
  return set_shout(self->conn, str);
}

static int pshoutobj_set_int(ShoutObjectAttr* attr, ShoutObject* self, PyObject* v) {
  long val;
  pshout_set_shout_int set_shout;

  if (!PyInt_Check(v)) {
    PyErr_SetString(PyExc_TypeError, "Numerical argument required");
    return -1;
  }
  
  val = PyLong_AsLong(v);
  set_shout = (pshout_set_shout_int)attr->set_shout;
  return set_shout(self->conn, val);
}

static int pshoutobj_set_bool(ShoutObjectAttr* attr, ShoutObject* self, PyObject* v) {
  long val;
  pshout_set_shout_int set_shout;

  if (!PyBool_Check(v)) {
    PyErr_SetString(PyExc_TypeError, "Boolean argument required");
    return -1;
  }

  val = (v == Py_True) ? 1 : 0;
  set_shout = (pshout_set_shout_int)attr->set_shout;
  return set_shout(self->conn, val);
}

static int pshoutobj_set_fmt(ShoutObjectAttr* attr, ShoutObject* self, PyObject* v) {
  const char* val;
  kv_strint* fmt_map;
  pshout_set_shout_int set_shout;

  if (!PyString_Check(v)) {
    PyErr_SetString(PyExc_TypeError, "String argument required");
    return SHOUTERR_INSANE;
  }

  val = PyString_AsString(v);
  for (fmt_map = ShoutFormatMap; fmt_map->name; fmt_map++) {
    if (!strcmp(fmt_map->name, val)) {
      set_shout = (pshout_set_shout_int)attr->set_shout;
      return set_shout(self->conn, fmt_map->val);
    }
  }

  PyErr_SetString(ShoutError, "Unsupported format");
  return SHOUTERR_UNSUPPORTED;
}

static int pshoutobj_set_proto(ShoutObjectAttr* attr, ShoutObject* self, PyObject* v) {
  const char* val;
  kv_strint* proto_map;
  pshout_set_shout_int set_shout;

  if (!PyString_Check(v)) {
    PyErr_SetString(PyExc_TypeError, "String argument required");
    return SHOUTERR_INSANE;
  }

  val = PyString_AsString(v);
  for (proto_map = ShoutProtocolMap; proto_map->name; proto_map++) {
    if (!strcmp(proto_map->name, val)) {
      set_shout = (pshout_set_shout_int)attr->set_shout;
      return set_shout(self->conn, proto_map->val);
    }
  }

  PyErr_SetString(ShoutError, "Unsupported protocol");
  return SHOUTERR_UNSUPPORTED;
}

static int pshoutobj_set_audio_info(ShoutObjectAttr* attr, ShoutObject* self, PyObject* v) {
  PyObject* key;
  PyObject* val;
  const char* skey;
  const char* sval;
  Py_ssize_t i = 0;
  int rc;

  if (!PyDict_Check(v)) {
    PyErr_SetString(PyExc_TypeError, "Dictionary argument required");
    return SHOUTERR_INSANE;
  }

  while (PyDict_Next(v, &i, &key, &val)) {
    if (!PyString_Check(key)) {
      PyErr_SetString(PyExc_TypeError, "Dictionary key must be string");
      return SHOUTERR_INSANE;
    }
    if (!PyString_Check(val)) {
      PyErr_SetString(PyExc_TypeError, "Dictionary value must be string");
      return SHOUTERR_INSANE;
    }

    skey = PyString_AsString(key);
    sval = PyString_AsString(val);

    if ((rc = shout_set_audio_info(self->conn, skey, sval)) != SHOUTERR_SUCCESS)
      return rc;
  }

  return SHOUTERR_SUCCESS;
}

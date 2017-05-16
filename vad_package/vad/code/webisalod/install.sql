
DB.DBA.VHOST_REMOVE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/SOAP');
DB.DBA.VHOST_REMOVE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/URIQA');
DB.DBA.VHOST_REMOVE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/XMLA');
DB.DBA.VHOST_REMOVE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/admin');
DB.DBA.VHOST_REMOVE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/bank');
DB.DBA.VHOST_REMOVE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/doc');
DB.DBA.VHOST_REMOVE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/images');
DB.DBA.VHOST_REMOVE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/install');
DB.DBA.VHOST_REMOVE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/issuer/key');
DB.DBA.VHOST_REMOVE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/mime');
DB.DBA.VHOST_REMOVE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/proxy');
DB.DBA.VHOST_REMOVE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/rdf_net');
DB.DBA.VHOST_REMOVE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/sparql-auth');
DB.DBA.VHOST_REMOVE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/sparql-graph-crud');
DB.DBA.VHOST_REMOVE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/sparql-graph-crud-auth');
DB.DBA.VHOST_REMOVE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/sparql-sd');
DB.DBA.VHOST_REMOVE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/uriqa');
DB.DBA.VHOST_REMOVE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/vsmx');

DB.DBA.VHOST_REMOVE (lhost=>'*sslini*',vhost=>'*sslini*',lpath=>'/DAV');
DB.DBA.VHOST_REMOVE (lhost=>'*sslini*',vhost=>'*sslini*',lpath=>'/SOAP');
DB.DBA.VHOST_REMOVE (lhost=>'*sslini*',vhost=>'*sslini*',lpath=>'/admin');
DB.DBA.VHOST_REMOVE (lhost=>'*sslini*',vhost=>'*sslini*',lpath=>'/conductor');
DB.DBA.VHOST_REMOVE (lhost=>'*sslini*',vhost=>'*sslini*',lpath=>'/doc');
DB.DBA.VHOST_REMOVE (lhost=>'*sslini*',vhost=>'*sslini*',lpath=>'/mime');
DB.DBA.VHOST_REMOVE (lhost=>'*sslini*',vhost=>'*sslini*',lpath=>'/vsmx');


DB.DBA.VHOST_REMOVE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/concept');

DB.DBA.VHOST_DEFINE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/concept',ppath=>'/DAV/VAD/webisalod/',is_dav=>1,opts=>vector('url_rewrite', 'http_rule_list_1'));


DB.DBA.URLREWRITE_CREATE_RULELIST ('http_rule_list_1', 1, vector ('http_rule_1', 'http_rule_2', 'http_rule_3'));
DB.DBA.URLREWRITE_CREATE_REGEX_RULE ( 'http_rule_1', 1, '(/[^#?]*)', vector ('par_1'), 1, '/DAV/VAD/webisalod/concept_desc.vsp?res=http://webisa.webdatacommons.org%U', vector ('par_1'), NULL, NULL, 0, 0, '' );
DB.DBA.URLREWRITE_CREATE_REGEX_RULE ( 'http_rule_2', 1, '(/[^#?]*)', vector ('par_1'), 1, '/DAV/VAD/webisalod/nquad.vsp?res=http://webisa.webdatacommons.org%U', vector ('par_1'), NULL, 'application/n-quads', 2, 0, '' );
DB.DBA.URLREWRITE_CREATE_REGEX_RULE ( 'http_rule_3', 1, '(/[^#?]*)', vector ('par_1'), 1, '/DAV/VAD/webisalod/csvquad.vsp?res=http://webisa.webdatacommons.org%U', vector ('par_1'), NULL, 'text/csv', 2, 0, '' );

DB.DBA.VHOST_DEFINE ( lhost=>'*ini*', vhost=>'*ini*', lpath=>'/webisalod_statics', ppath=>'/DAV/VAD/webisalod/webisalod_statics/', is_dav=>1,def_page=>'index.html');

DB.DBA.VHOST_DEFINE (lhost=>'*ini*',vhost=>'*ini*',lpath=>'/',ppath=>'/DAV/VAD/webisalod/',is_dav=>1, def_page=>'index.html', opts=>vector ('url_rewrite', 'http_rule_list_2'));
DB.DBA.URLREWRITE_CREATE_RULELIST ( 'http_rule_list_2', 1, vector ('http_rule_4'));
DB.DBA.URLREWRITE_CREATE_REGEX_RULE ( 'http_rule_4', 1, '(/[^#?]+)', vector ('par_1'), 1, '/DAV/VAD/webisalod/triple_desc.vsp?res=http://webisa.webdatacommons.org%U', vector ('par_1'), NULL, NULL, 2, 0, '' );
    
DB.DBA.VHOST_DEFINE (lhost=>'*ini*', vhost=>'*ini*', lpath=>'/nquad',ppath=>'/DAV/VAD/webisalod/', is_dav=>1, def_page=>'nquad.vsp', vsp_user=>'dba');
DB.DBA.VHOST_DEFINE (lhost=>'*ini*', vhost=>'*ini*', lpath=>'/csvquad',ppath=>'/DAV/VAD/webisalod/', is_dav=>1, def_page=>'csvquad.vsp', vsp_user=>'dba');



create procedure get_string_representation_of_object(in _object any) returns varchar {
again:
    if(__tag(_object) = 246){
        declare dat any;
        dat := __rdf_sqlval_of_obj (_object, 1);
        _object := dat;
        goto again;
    }else if(__tag(_object) = 189){
        return sprintf('%d', _object);
    }else if(__tag(_object) = 190){
        return sprintf('%f', _object);
    }else if(__tag(_object) = 191){
        return sprintf('%f', _object);
    }else if(__tag(_object) = 219){
        return sprintf('%s', cast (_object as varchar));
    }else if (__tag(_object) = 182){
        declare str_out any;
        str_out := string_output();
        http_value(charset_recode(_object, 'UTF-8', '_WIDE_'), null, str_out);
        return string_output_string(str_out);
    }else if(__tag(_object) = 211){
        return sprintf('%s', datestring (_object));
    }else if (__tag (_object) = 243){
        return id_to_iri(_object);
    }else if(__tag(_object) = 238){
        return st_astext(_object);
    }else {
        return sprintf('FIXME %i', __tag (_object));
    }
}